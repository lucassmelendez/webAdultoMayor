from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.http import JsonResponse
from .models import Taller, Inscripcion
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import Http404


def register(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        rut = request.POST['rut']
        primer_nombre = request.POST['primer_nombre']
        segundo_nombre = request.POST['segundo_nombre']
        primer_apellido = request.POST['primer_apellido']
        segundo_apellido = request.POST['segundo_apellido']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        telefono = request.POST['telefono']
        direccion = request.POST['direccion']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # Validar contraseñas
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'register.html')
        
        # Verificar si el nombre de usuario ya está tomado
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return render(request, 'register.html')
        
        # Verificar si el correo electrónico ya está registrado
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, 'register.html')
        
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')  # Ajusta el formato si es necesario

# Obtienes la fecha actual
        fecha_actual = datetime.now()

# Calculas la diferencia de años entre la fecha actual y la fecha de nacimiento
        edad = (fecha_actual - fecha_nacimiento).days // 365  # Aproximación de edad en años

# Verificas si la persona tiene 60 años o más
        if edad < 60:
            messages.error(request, "La edad debe ser mayor a 60 años")
            return render(request, 'register.html')
        
        # Crear el nuevo usuario
        try:
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password1,
                first_name=primer_nombre,
                last_name=primer_apellido
            )
            
            # Crear el perfil del usuario
            user_profile = UserProfile.objects.create(
                user=user,
                rut=rut,
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                fecha_nacimiento=fecha_nacimiento,
                telefono=telefono,
                direccion=direccion,
            )
            
            messages.success(request, "Te has registrado exitosamente.")
            return redirect('login')  # Redirigir al login
        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {e}")
            return render(request, 'register.html')

    return render(request, 'register.html')

def index(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None
    else:
        user_profile = None

    return render(request, 'index.html', {'user_profile': user_profile})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Si la autenticación es exitosa, iniciar sesión
            login(request, user)
            return redirect('index')  # Redirigir al inicio después de login exitoso
        else:
            # Si las credenciales son incorrectas, mostrar mensaje de error
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, 'login.html')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)  # Cerrar la sesión del usuario
    return redirect('index')

@login_required
def talleres(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'talleres.html', {'user_profile': user_profile})

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # Elimina el usuario
        return redirect('index')  # Redirige al inicio después de eliminar
    return redirect('profile')  # Si no es POST, redirige al perfil

@login_required
def update_profile(request):
    # Obtener el perfil del usuario
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        raise Http404("Perfil no encontrado")

    if request.method == 'POST':
        # Recuperar los datos del formulario desde request.POST
        rut = request.POST.get('rut', user_profile.rut)
        primer_nombre = request.POST.get('primer_nombre', user_profile.primer_nombre)
        segundo_nombre = request.POST.get('segundo_nombre', user_profile.segundo_nombre)
        primer_apellido = request.POST.get('primer_apellido', user_profile.primer_apellido)
        segundo_apellido = request.POST.get('segundo_apellido', user_profile.segundo_apellido)
        fecha_nacimiento = request.POST.get('fecha_nacimiento', user_profile.fecha_nacimiento)
        telefono = request.POST.get('telefono', user_profile.telefono)
        direccion = request.POST.get('direccion', user_profile.direccion)

        # Actualizar los campos del perfil
        user_profile.rut = rut
        user_profile.primer_nombre = primer_nombre
        user_profile.segundo_nombre = segundo_nombre
        user_profile.primer_apellido = primer_apellido
        user_profile.segundo_apellido = segundo_apellido
        user_profile.fecha_nacimiento = fecha_nacimiento
        user_profile.telefono = telefono
        user_profile.direccion = direccion
        
        # Guardar los cambios
        user_profile.save()

        # Mostrar un mensaje de éxito y redirigir al perfil
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('profile')

    else:
        # Si es un GET, pre-cargar el formulario con los datos actuales del perfil
        return render(request, 'profile/update_profile.html', {'user_profile': user_profile})



@login_required
def toggle_inscripcion(request, taller_id):
    try:
        # Obtener el taller usando el ID
        taller = get_object_or_404(Taller, id=taller_id)
        
        # Intentar obtener o crear la inscripción
        inscripcion, created = Inscripcion.objects.get_or_create(user=request.user, taller=taller)

        if created:
            # Si la inscripción es nueva (se creó), enviamos una respuesta positiva
            return JsonResponse({'status': 'added', 'message': 'Inscripción exitosa.'})
        else:
            # Si la inscripción ya existía (es decir, el usuario estaba inscrito), la eliminamos
            inscripcion.delete()
            return JsonResponse({'status': 'removed', 'message': 'Desinscripción exitosa.'})
    
    except Exception as e:
        # Si ocurre algún error, devolveremos un error
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def lista_talleres(request):
    talleres = Taller.objects.all()
    talleres_inscritos = (
        Inscripcion.objects.filter(user=request.user).values_list('taller_id', flat=True)
        if request.user.is_authenticated else []
    )
    return render(request, 'talleres.html', {'talleres': talleres, 'talleres_inscritos': talleres_inscritos})