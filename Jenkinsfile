pipeline {
    agent any

    stages {
        stage('Diagnose Environment') {
            steps {
                bat '''
                    echo === PATH ===
                    echo %PATH%

                    echo === WHERE PYTHON ===
                    where python || echo python not found

                    echo === WHERE PY ===
                    where py || echo py launcher not found

                    echo === PROGRAM FILES PYTHON ===
                    dir "C:\\Program Files\\Python*" /b || echo No system Python installation found
                '''
            }
        }
    }
}