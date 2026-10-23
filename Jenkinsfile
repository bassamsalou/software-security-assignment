pipeline {
    agent any

    environment {
        PATH = "C:\\Users\\Bruger\\AppData\\Local\\Programs\\Python\\Python311;C:\\Users\\Bruger\\AppData\\Local\\Programs\\Python\\Python311\\Scripts;${env.PATH}"
    }

    stages {
        stage('Validate Environment') {
            steps {
                bat 'where python'
                bat 'python --version'
                bat 'python -m pip --version'
            }
        }
    }
}