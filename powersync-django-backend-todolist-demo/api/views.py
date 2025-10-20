from django.utils import timezone
import json
from venv import logger
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
import api.app_utils as app_utils
from .models import Todos, Lists
from django.contrib.auth import get_user_model


@api_view(['GET'])
def get_powersync_token(request):
    try:
        # Get user_id from query params (for client compatibility)
        user_id = request.GET.get('user_id', "1")
        
        # For demo purposes, if user_id is not found, use default
        # In your app you'll fetch the user from the database
        token = app_utils.create_jwt_token(user_id)
        return JsonResponse({
            "token": token,
            "powersync_url": app_utils.power_sync_url
        }, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def get_keys(request):
    try:
        return JsonResponse({
            "keys": [
                app_utils.power_sync_public_key_json
            ]
        }, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def get_session(request):
    try:
        # For demo purposes the session is always valid,
        # In your app you'll need to handle user sessions
        # and invalidate the session after expiry.
        return JsonResponse({
            "session": "valid"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def auth(request):
    # For demo purposes the username and password are in plain text,
    # In your app you must handle usernames and passwords properly.
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            token = app_utils.create_jwt_token(user.id)
            response = {'access_token': token}
            return JsonResponse(response, status=200)
        else:
            logger.warning(f"Authentication failed for username: {username}")
            return JsonResponse({'message': 'Authentication failed'}, status=401)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({'message': 'Internal server error'}, status=500)


@csrf_exempt
def register(request):
    # For demo purposes the username and password are in plain text,
    # In your app you must handle usernames and passwords properly.
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    try:
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                password=password,
                last_login=timezone.now()
            )
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'message': 'Username is taken'}, status=401)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({'message': 'Internal server error'}, status=500)


@csrf_exempt
@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
def upload_data(request):
    """
    Handle data uploads from PowerSync client.
    Supports both batch format (from web client) and single operation format.
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
        print(f"=== UPLOAD_DATA REQUEST ===")
        print(f"Method: {request.method}")
        print(f"Body: {json.dumps(body, indent=2)}")
        
        # Check if this is a batch operation
        # The client can send either 'batch' or 'data' as the array key
        operations = body.get('batch') or body.get('data')
        
        if operations:
            # Process batch operations
            print(f"Processing batch with {len(operations)} operations")
            for op in operations:
                print(f"  Operation: {op.get('op')} on {op.get('table')} - ID: {op.get('id')}")
                process_operation(op, request.method)
            return JsonResponse({'message': 'Batch processed successfully'}, status=200)
        else:
            # Single operation (legacy format)
            print(f"Processing single operation: {body.get('table')}")
            process_operation(body, request.method)
            return JsonResponse({'message': 'Operation processed successfully'}, status=200)
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({'message': str(e)}, status=500)


def process_operation(op, method_override=None):
    """
    Process a single operation (either from batch or direct call).
    Op format: { 'op': 'PUT'|'PATCH'|'DELETE', 'table': 'todos'|'lists', 'id': '...', 'data': {...} }
    """
    operation = op.get('op', method_override)
    table = op.get('table')
    data = op.get('data', {})
    
    # Add the id from the operation to the data if not present
    if 'id' in op and 'id' not in data:
        data['id'] = op['id']
    
    if table == 'todos':
        if operation == 'PUT':
            upsertTodo(data)
        elif operation == 'PATCH':
            updateTodo(data)
        elif operation == 'DELETE':
            try:
                todo = Todos.objects.get(id=data.get('id'))
                todo.delete()
            except Todos.DoesNotExist:
                pass  # Silently ignore if doesn't exist
    elif table == 'lists':
        if operation == 'PUT':
            upsertList(data)
        elif operation == 'PATCH':
            updateList(data)
        elif operation == 'DELETE':
            try:
                list_obj = Lists.objects.get(id=data.get('id'))
                list_obj.delete()
            except Lists.DoesNotExist:
                pass  # Silently ignore if doesn't exist


def upsertTodo(data):
    try:
        todo = Todos.objects.get(id=data.get('id'))
        todo.description = data.get('description')
        todo.created_by = data.get('created_by')
        todo.list_id = data.get('list_id')
        todo.save()
    except Todos.DoesNotExist:
        todo = Todos(id=data.get('id'), description=data.get(
            'description'), created_by=data.get('created_by'), list_id=data.get('list_id'))
        todo.save()


def updateTodo(data):
    todo = Todos.objects.get(id=data.get('id'))
    if todo is not None:
        if 'description' in data:
            todo.description = data.get('description')
        if 'created_by' in data:
            todo.created_by = data.get('created_by')
        if 'list_id' in data:
            todo.list_id = data.get('list_id')
        if 'completed' in data:
            todo.completed = data.get('completed')
        if 'completed_by' in data:
            todo.completed_by = data.get('completed_by')
        if 'completed_at' in data:
            todo.completed_at = data.get('completed_at')
        todo.save()


def upsertList(data):
    try:
        list = Lists.objects.get(id=data.get('id'))
        list.created_at = data.get('created_at')
        list.name = data.get('name')
        list.owner_id = data.get('owner_id')
        list.save()
        return Response({'message': 'List updated'}, status=200)
    except Lists.DoesNotExist:
        list = Lists(id=data.get('id'), created_at=data.get(
            'created_at'), name=data.get('name'), owner_id=data.get('owner_id'))
        list.save()


def updateList(data):
    list = Lists.objects.get(id=data.get('id'))
    if list is not None:
        list.created_at = data.get('created_at')
        list.name = data.get('name')
        list.owner_id = data.get('owner_id')
        list.save()
