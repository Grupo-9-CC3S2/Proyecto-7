resource "null_resource" "service_1" {
    provisioner "local-exec" {
        command = "echo 'Ejemplo de servicio 1' > service_1.txt"
    }
}

resource "null_resource" "service_2" {
    provisioner "local-exec" {
        command = "echo 'Ejemplo de servicio 2' > service_2.txt"
    }
}

resource "null_resource" "service_3" {
    provisioner "local-exec" {
        command = "echo 'Ejemplo de servicio 3' > service_3.txt"
    }
}