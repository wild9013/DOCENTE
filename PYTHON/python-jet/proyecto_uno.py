import flet as ft

def main(page: ft.Page):
    # Crear campos de texto
    name_field = ft.TextField(label="Nombre", hint_text="Ingresa tu nombre")
    number_field = ft.TextField(label="Número", hint_text="Ingresa un número", keyboard_type=ft.KeyboardType.NUMBER)

    # Crear un texto para mostrar el resultado
    result_text = ft.Text()

    # Función para manejar el clic del botón
    def on_button_click(e):
        name = name_field.value
        number = number_field.value
        if name and number:
            result_text.value = f"Nombre: {name}, Número: {number}"
        else:
            result_text.value = "Por favor, completa ambos campos."
        page.update()

    # Crear el botón
    submit_button = ft.ElevatedButton(text="Mostrar", on_click=on_button_click)

    # Agregar todo al contenido de la página
    page.add(
        name_field,
        number_field,
        submit_button,
        result_text
    )

# Ejecutar la aplicación
ft.app(target=main)
