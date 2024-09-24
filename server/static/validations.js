document.addEventListener("DOMContentLoaded", function() {
    console.log("Validations script loaded successfully!");

    // Validación del formulario de registro
    document.getElementById("registerForm").addEventListener("submit", function(event) {
        let valid = true;

        // Validar nombre (solo letras y espacios, mínimo 2 caracteres)
        let name = document.getElementById("name").value.trim();
        if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(name) || name.length < 2) {
            Swal.fire("Error", "El nombre debe contener solo letras (sin números ni caracteres especiales) y tener al menos 2 caracteres.", "error");
            valid = false;
        }

        // Validar apellido (solo letras y espacios)
        let lastname = document.getElementById("lastname").value.trim();
        if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(lastname) || lastname.length < 2) {
            Swal.fire("Error", "El apellido debe contener solo letras (sin números ni caracteres especiales) y tener al menos 2 caracteres.", "error");
            valid = false;
        }

        // Validar correo
        let gmail = document.getElementById("gmail").value.trim();
        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(gmail)) {
            Swal.fire("Error", "Por favor ingrese un correo con formato valido ejemplo : correo@gmail.com", "error");
            valid = false;
        }

        // Validar nombre de usuario (mínimo 4 caracteres)
        let username = document.getElementById("username").value.trim();
        if (username.length < 4) {
            Swal.fire("Error", "El nombre de usuario debe tener al menos 4 caracteres", "error");
            valid = false;
        }

        // Validar contraseña (mínimo 8 caracteres)
        let password = document.getElementById("password").value.trim();
        if (password.length < 8) {
            Swal.fire("Error", "La contraseña debe tener al menos 8 caracteres", "error");
            valid = false;
        }

        // Si alguna validación falla, evitar que se envíe el formulario
        if (!valid) {
            event.preventDefault();
        }
    });

    // Validación del formulario de inicio de sesión
    document.getElementById("loginForm").addEventListener("submit", function(event) {
        let valid = true;

        // Validar nombre de usuario (mínimo 4 caracteres)
        let username = document.getElementById("loginUsername").value.trim();
        if (username.length < 4) {
            Swal.fire("Error", "El nombre de usuario debe tener al menos 4 caracteres", "error");
            valid = false;
        }

        // Validar contraseña (mínimo 8 caracteres)
        let password = document.getElementById("loginPassword").value.trim();
        if (password.length < 8) {
            Swal.fire("Error", "La contraseña debe tener al menos 8 caracteres", "error");
            valid = false;
        }

        // Si alguna validación falla, evitar que se envíe el formulario
        if (!valid) {
            event.preventDefault();
        }
    });

    document.getElementById("profileForm").addEventListener("submit", function(event) {
        let valid = true;
    
        // Validar correo
        let gmail = document.getElementById("gmail").value.trim();
        let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(gmail)) {
            Swal.fire("Error", "Por favor ingresa un correo con formato valido", "error");
            valid = false;
        }
    
        // Validar contraseña (mínimo 8 caracteres si se ingresa)
        let password = document.getElementById("password").value.trim();
        if (password.length > 0 && password.length < 8) {
            Swal.fire("Error", "La contraseña debe tener al menos 8 caracteres", "error");
            valid = false;
        }
    
        // Si alguna validación falla, evitar que se envíe el formulario
        if (!valid) {
            event.preventDefault();
        }
    });
});
