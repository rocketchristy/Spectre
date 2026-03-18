pipeline {
  agent any

  stages {
    stage('Install dependencies') {
      steps {
        sh 'npm install'
      }
    }

    stage('Run frontend tests') {
      steps {
        sh 'npm run test'
      }
    }
  }
}