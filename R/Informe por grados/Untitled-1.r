# Instala los paquetes si aC:n no lo has hecho
#install.packages("pdftools")
#install.packages("stringr")

# Carga las librerC-as
library(pdftools)
library(stringr)

# Ruta al archivo PDF
pdf_file <- "archivo.pdf"

# Extraer texto del PDF
pdf_text <- pdf_text(pdf_file)

# Ver el texto extraC-do (opcional)
print(pdf_text)

