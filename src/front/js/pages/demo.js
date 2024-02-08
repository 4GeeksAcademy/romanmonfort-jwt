import React, { useEffect, useState } from 'react';


function PrivateView() {
    const [userData, setUserData] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');

        if (token) {
            // Si hay un token en localStorage, puedes usarlo para hacer una solicitud a la ruta protegida
            fetchProtectedData(token);
        } else {
            // Si no hay token, redirige al usuario a la página de inicio de sesión
            // Por ejemplo:
            // history.push('/login');
        }
    }, []);

    const fetchProtectedData = async (token) => {
        try {
            const response = await fetch(`https://bookish-trout-5gqqq54p45v5f4xwv-3001.app.github.dev/protected`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.msg);
            }

            const data = await response.json();
            setUserData(data.user);

        } catch (error) {
            console.error('Error fetching protected data:', error);
            // Podrías manejar el error de alguna manera, como redirigir al usuario a la página de inicio de sesión
            // Por ejemplo:
            // history.push('/login');
        }
    };

    return (
        <div>
            {userData ? (
                <div>
                    <h2>Bienvenido {userData},su token se guardo correctamente en el localStorage.</h2>
                    {/* Otros datos del usuario */}
                </div>
            ) : (
                <p>Cargando...</p>
            )}
        </div>
    );
}

export default PrivateView;
