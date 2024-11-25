import pytest
import requests

BASE_URL = "http://vikunja:3456/api/v1"


def register():
    register_payload = {
        "email": "testuser@testuser.com",
        "id": 0,
        "password": "123123123",
        "username": "testuser"
    }

    # Конечная точка для регистрации
    register_url = f"{BASE_URL}/register"

    # Отправка запроса на регистрацию
    register_response = requests.post(register_url, json=register_payload)
    if register_response.status_code == 400 and "already exists" in register_response.text.lower():
        return
    assert register_response.status_code == 200, f"Ошибка регистрации. Код: {register_response.status_code}"



def login():
    login_payload = {
        "long_token": True,
        "password": "123123123",
        "username": "testuser"
    }

    # Конечная точка для авторизации
    login_url = f"{BASE_URL}/login"

    # Отправка запроса на авторизацию
    login_response = requests.post(login_url, json=login_payload)

    assert login_response.status_code == 200, f"Ошибка регистрации. Код: {login_response.status_code}"
    token = login_response.json().get("token")
    assert token, "Токен отсутствует в ответе сервера"
    return token

def create_project(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    create_project_payload = {
        "identifier": "Project",
        "title": "Project",
    }
    create_project_url = f"{BASE_URL}/projects"

    # Отправка запроса на регистрацию
    create_project_response = requests.put(create_project_url, json=create_project_payload, headers=headers)
    assert create_project_response.status_code == 201, f"Ошибка создания проекта. Код: {create_project_response.status_code}"
    response_data = create_project_response.json()
    project_id = response_data.get("id")
    view_id = response_data.get("views", [])[0]["id"]
    return project_id, view_id

@pytest.fixture(scope="module")
def token():
    register()
    return login()

@pytest.fixture(scope="module")
def project(token):
    project_id, view_id = create_project(token)
    return {
        "project_id": project_id,
        "view_id": view_id
    }

@pytest.fixture(scope="module", autouse=True)
def delete_project(token, project):
    yield
    project_id = project["project_id"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    delete_project_url = f"{BASE_URL}/projects/{project_id}"
    response = requests.delete(delete_project_url, headers=headers)
    assert response.status_code == 200, f"Ошибка удаления проекта. Код: {response.status_code}"


# Тест создания задачи
def test_create_task(token, project):
    project_id = project["project_id"]
    task_payload = {
        "project_id": project_id,
        "title": "Test"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    create_task_url = f"{BASE_URL}/projects/{project_id}/tasks"

    response = requests.put(create_task_url, json=task_payload, headers=headers)
    assert response.status_code == 201, f"Ошибка создания задачи. Код: {response.status_code}"

    task_data = response.json()
    task_id = task_data['id']

    # Проверим, что задача действительно была создана
    task_get_url = f"{BASE_URL}/tasks/{task_id}"
    task_response = requests.get(task_get_url, headers=headers)

    assert task_response.status_code == 200, f"Ошибка получения задачи. Код: {task_response.status_code}"
    task = task_response.json()
    assert task[
               'title'] == "Test", f"Название задачи не совпадает. Ожидалось 'Test', а получено {task['title']}"

def test_create_task_with_empty_title(token, project):
    project_id = project["project_id"]
    task_payload = {
        "project_id": project_id,
        "title": "     "
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    create_task_url = f"{BASE_URL}/projects/{project_id}/tasks"

    response = requests.put(create_task_url, json=task_payload, headers=headers)
    assert response.status_code == 201, f"Ошибка создания задачи. Код: {response.status_code}"

    task_data = response.json()
    task_id = task_data['id']

    # Проверим, что задача действительно была создана
    task_get_url = f"{BASE_URL}/tasks/{task_id}"
    task_response = requests.get(task_get_url, headers=headers)

    assert task_response.status_code == 200, f"Ошибка получения задачи. Код: {task_response.status_code}"
    task = task_response.json()
    assert task[
               'title'] == "     ", f"Название задачи не совпадает. Ожидалось '     ', а получено {task['title']}"

def test_create_task_with_invalid_title(token, project):
    project_id = project["project_id"]
    task_payload = {
        "project_id": project_id,
        "title": "*\\"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    create_task_url = f"{BASE_URL}/projects/{project_id}/tasks"

    response = requests.put(create_task_url, json=task_payload, headers=headers)
    assert response.status_code == 201, f"Ошибка создания задачи. Код: {response.status_code}"

    task_data = response.json()
    task_id = task_data['id']

    # Проверим, что задача действительно была создана
    task_get_url = f"{BASE_URL}/tasks/{task_id}"
    task_response = requests.get(task_get_url, headers=headers)

    assert task_response.status_code == 200, f"Ошибка получения задачи. Код: {task_response.status_code}"
    task = task_response.json()
    assert task[
               'title'] == "*\\", f"Название задачи не совпадает. Ожидалось '*\\', а получено {task['title']}"

# Тест чтения задач (Read Task)
def test_read_task(token, project):
    project_id = project["project_id"]
    view_id = project["view_id"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    task_get_url = f"{BASE_URL}/projects/{project_id}/views/{view_id}/tasks"

    response = requests.get(task_get_url, headers=headers)
    assert response.status_code == 200, f"Ошибка чтения задач. Код: {response.status_code}"

    tasks = response.json()
    assert len(tasks) > 0, "Задачи не найдены"
    assert 'title' in tasks[0], "Отсутствует поле 'title' у задачи"


# Тест обновления задачи (Update Task)
def test_update_task(token, project):
    project_id = project["project_id"]
    task_payload = {
        "project_id": project_id,
        "title": "Test2"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Создаем задачу, которую будем обновлять
    create_task_url = f"{BASE_URL}/projects/{project_id}/tasks"
    response = requests.put(create_task_url, json=task_payload, headers=headers)
    assert response.status_code == 201, f"Ошибка создания задачи. Код: {response.status_code}"

    task_data = response.json()
    task_id = task_data['id']

    # Обновляем задачу
    update_task_payload = {
        "title": "Updated Test2",
    }

    update_task_url = f"{BASE_URL}/tasks/{task_id}"
    update_response = requests.post(update_task_url, json=update_task_payload, headers=headers)

    assert update_response.status_code == 200, f"Ошибка обновления задачи. Код: {update_response.status_code}"

    # Проверяем, что задача обновлена
    task_get_url = f"{BASE_URL}/tasks/{task_id}"
    task_response = requests.get(task_get_url, headers=headers)

    assert task_response.status_code == 200, f"Ошибка получения обновленной задачи. Код: {task_response.status_code}"
    task = task_response.json()
    assert task[
               'title'] == "Updated Test2", f"Название задачи не обновилось. Ожидалось 'Updated Test2', а получено {task['title']}"


# Тест удаления задачи (Delete Task)
def test_delete_task(token, project):
    project_id = project["project_id"]
    task_payload = {
        "project_id": project_id,
        "title": "Task for delete"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Создаем задачу, которую будем удалять
    create_task_url = f"{BASE_URL}/projects/{project_id}/tasks"
    response = requests.put(create_task_url, json=task_payload, headers=headers)
    assert response.status_code == 201, f"Ошибка создания задачи. Код: {response.status_code}"

    task_data = response.json()
    task_id = task_data['id']

    # Удаляем задачу
    delete_task_url = f"{BASE_URL}/tasks/{task_id}"
    delete_response = requests.delete(delete_task_url, headers=headers)

    assert delete_response.status_code == 200, f"Ошибка удаления задачи. Код: {delete_response.status_code}"

    # Проверяем, что задача действительно удалена
    task_get_url = f"{BASE_URL}/tasks/{task_id}"
    task_response = requests.get(task_get_url, headers=headers)

    assert task_response.status_code == 404, f"Задача не была удалена. Код: {task_response.status_code}"


