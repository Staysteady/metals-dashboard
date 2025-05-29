import '@testing-library/jest-dom';
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './mocks/server';

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));

// Reset handlers after each test `important for test isolation`
afterEach(() => server.resetHandlers());

// Clean up after all tests are done
afterAll(() => server.close()); 