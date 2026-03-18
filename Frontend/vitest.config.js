import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      // Use jsdom for DOM testing
      environment: 'jsdom',
      
      // Exclude patterns
      exclude: [...configDefaults.exclude, 'e2e/**'],
      
      // Root directory for tests
      root: fileURLToPath(new URL('./', import.meta.url)),
      
      // Global test setup
      setupFiles: ['./src/test/setup.js'],
      
      // Make test globals available (describe, it, expect, etc.)
      globals: true,
      
      // Coverage configuration
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html', 'lcov'],
        exclude: [
          ...configDefaults.coverage.exclude,
          'src/test/**',
          '**/*.test.js',
          '**/*.spec.js',
          '**/node_modules/**',
          'dist/**',
        ],
        thresholds: {
          lines: 70,
          branches: 60,
          functions: 70,
          statements: 70,
        },
      },
      
      // Test timeouts
      testTimeout: 10000,
      hookTimeout: 10000,
    },
  }),
)
