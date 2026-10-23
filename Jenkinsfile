pipeline {
    agent any

    stages {
        stage('Validate Environment') {
            steps {
                bat 'python --version'
                bat 'python -m pip --version'
            }
        }
    }
}