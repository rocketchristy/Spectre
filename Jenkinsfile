pipeline {
  agent any

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  environment {
    NODEJS_VERSION = '22'
    PYTHON_VERSION = '3.11'
  }

  stages {
    stage('Checkout') {
      steps {
        echo "Checking out code from repository..."
        checkout scm
      }
    }

    stage('Install Frontend Dependencies') {
      steps {
        dir('Frontend') {
          echo "Installing Frontend dependencies..."
          bat 'npm install'
        }
      }
    }

    stage('Frontend Lint') {
      steps {
        dir('Frontend') {
          echo "Running Frontend linting..."
          bat 'npm run lint'
        }
      }
    }

    stage('Frontend Unit Tests') {
      steps {
        dir('Frontend') {
          echo "Running Frontend unit tests with Vitest..."
          bat 'npm run test:unit'
        }
      }
    }

    stage('Frontend Build') {
      steps {
        dir('Frontend') {
          echo "Building Frontend..."
          bat 'npm run build'
        }
      }
    }
  }

  post {
    always {
      echo "Pipeline completed"
    }

    success {
      echo "✓ All tests passed successfully"
    }

    failure {
      echo "✗ Pipeline failed - check logs above"
    }

    cleanup {
      cleanWs()
    }
  }
}
