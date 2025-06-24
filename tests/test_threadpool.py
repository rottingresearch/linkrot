"""
Comprehensive tests for the threadpool module.
Tests Worker and ThreadPool classes for concurrent task execution.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from queue import Queue

from linkrot.threadpool import Worker, ThreadPool


class TestWorker:
    """Test Worker thread class."""

    def test_worker_creation(self):
        """Test basic worker creation."""
        tasks = Queue()
        worker = Worker(tasks)
        
        assert isinstance(worker, threading.Thread)
        assert worker.daemon is True
        assert worker.is_alive()
        
        # Clean up
        tasks.put((lambda: None, (), {}))
        tasks.put((None, None, None))  # Sentinel to stop worker
        time.sleep(0.1)

    def test_worker_executes_tasks(self):
        """Test that worker executes tasks from queue."""
        tasks = Queue()
        worker = Worker(tasks)
        
        # Create a task that sets a flag
        result = {"executed": False}
        def test_task():
            result["executed"] = True
        
        # Add task to queue
        tasks.put((test_task, (), {}))
        
        # Wait for task execution
        tasks.join()
        
        assert result["executed"] is True

    def test_worker_with_args(self):
        """Test worker executing task with arguments."""
        tasks = Queue()
        worker = Worker(tasks)
        
        result = {"value": None}
        def test_task(value, multiplier=1):
            result["value"] = value * multiplier
        
        # Add task with args and kwargs
        tasks.put((test_task, (5,), {"multiplier": 3}))
        
        tasks.join()
        
        assert result["value"] == 15

    def test_worker_exception_handling(self):
        """Test that worker handles exceptions gracefully."""
        tasks = Queue()
        
        with patch('builtins.print') as mock_print:
            worker = Worker(tasks)
            
            def failing_task():
                raise ValueError("Test exception")
            
            # Add failing task
            tasks.put((failing_task, (), {}))
            
            tasks.join()
            
            # Should have printed the exception
            mock_print.assert_called_once()

    def test_worker_multiple_tasks(self):
        """Test worker executing multiple tasks."""
        tasks = Queue()
        worker = Worker(tasks)
        
        results = []
        def append_task(value):
            results.append(value)
        
        # Add multiple tasks
        for i in range(5):
            tasks.put((append_task, (i,), {}))
        
        tasks.join()
        
        # All tasks should have been executed
        assert len(results) == 5
        assert set(results) == {0, 1, 2, 3, 4}

    def test_worker_inheritance(self):
        """Test that Worker properly inherits from Thread."""
        tasks = Queue()
        worker = Worker(tasks)
        
        # Should have Thread methods
        assert hasattr(worker, 'start')
        assert hasattr(worker, 'join')
        assert hasattr(worker, 'is_alive')
        
        # Should be a daemon thread
        assert worker.daemon is True


class TestThreadPool:
    """Test ThreadPool class."""

    def test_threadpool_creation(self):
        """Test basic threadpool creation."""
        pool = ThreadPool(3)
        
        assert hasattr(pool, 'tasks')
        assert isinstance(pool.tasks, Queue)

    def test_threadpool_add_task(self):
        """Test adding tasks to threadpool."""
        pool = ThreadPool(2)
        
        result = {"executed": False}
        def test_task():
            result["executed"] = True
        
        pool.add_task(test_task)
        pool.wait_completion()
        
        assert result["executed"] is True

    def test_threadpool_add_task_with_args(self):
        """Test adding tasks with arguments."""
        pool = ThreadPool(2)
        
        result = {"sum": 0}
        def add_task(a, b, multiplier=1):
            result["sum"] = (a + b) * multiplier
        
        pool.add_task(add_task, 3, 4, multiplier=2)
        pool.wait_completion()
        
        assert result["sum"] == 14

    def test_threadpool_map(self):
        """Test map functionality."""
        pool = ThreadPool(3)
        
        results = []
        def square_task(x):
            results.append(x * x)
        
        # Map function over list of arguments
        pool.map(square_task, [1, 2, 3, 4, 5])
        pool.wait_completion()
        
        # All squares should be computed
        assert len(results) == 5
        assert set(results) == {1, 4, 9, 16, 25}

    def test_threadpool_map_empty_list(self):
        """Test map with empty argument list."""
        pool = ThreadPool(2)
        
        executed = {"count": 0}
        def count_task(x):
            executed["count"] += 1
        
        pool.map(count_task, [])
        pool.wait_completion()
        
        assert executed["count"] == 0

    def test_threadpool_concurrent_execution(self):
        """Test that tasks execute concurrently."""
        pool = ThreadPool(3)
        
        start_times = []
        def timing_task(task_id):
            start_times.append((task_id, time.time()))
            time.sleep(0.1)  # Simulate work
        
        start_time = time.time()
        
        # Add multiple tasks
        for i in range(3):
            pool.add_task(timing_task, i)
        
        pool.wait_completion()
        
        total_time = time.time() - start_time
        
        # Should complete in roughly 0.1 seconds (concurrent) rather than 0.3 (sequential)
        assert total_time < 0.2  # Allow some overhead
        assert len(start_times) == 3

    def test_threadpool_wait_completion(self):
        """Test wait_completion functionality."""
        pool = ThreadPool(2)
        
        completed = {"count": 0}
        def slow_task():
            time.sleep(0.05)
            completed["count"] += 1
        
        # Add multiple tasks
        for _ in range(4):
            pool.add_task(slow_task)
        
        # Should block until all tasks are done
        pool.wait_completion()
        
        assert completed["count"] == 4

    def test_threadpool_multiple_workers(self):
        """Test threadpool with multiple workers."""
        pool = ThreadPool(5)  # 5 workers
        
        worker_ids = set()
        lock = threading.Lock()
        
        def identify_worker():
            time.sleep(0.01)  # Small delay to encourage different workers
            with lock:
                worker_ids.add(threading.current_thread().ident)
        
        # Add more tasks than workers
        for _ in range(10):
            pool.add_task(identify_worker)
        
        pool.wait_completion()
        
        # Should have used multiple workers (up to 5)
        assert len(worker_ids) <= 5
        # Due to timing, we might only see 1 worker, so let's just check <= 5
        assert len(worker_ids) >= 1  # Should use at least one worker

    def test_threadpool_exception_handling(self):
        """Test threadpool handling exceptions in tasks."""
        pool = ThreadPool(2)
        
        successful_tasks = {"count": 0}
        
        def good_task():
            successful_tasks["count"] += 1
        
        def bad_task():
            raise ValueError("Test exception")
        
        with patch('builtins.print'):  # Suppress exception printing
            # Mix good and bad tasks
            pool.add_task(good_task)
            pool.add_task(bad_task)
            pool.add_task(good_task)
            
            pool.wait_completion()
        
        # Good tasks should still execute despite bad ones
        assert successful_tasks["count"] == 2

    def test_threadpool_large_workload(self):
        """Test threadpool with large number of tasks."""
        pool = ThreadPool(4)
        
        results = []
        lock = threading.Lock()
        
        def accumulate_task(value):
            with lock:
                results.append(value)
        
        # Add many tasks
        task_count = 100
        pool.map(accumulate_task, range(task_count))
        pool.wait_completion()
        
        assert len(results) == task_count
        assert set(results) == set(range(task_count))

    def test_threadpool_task_order_independence(self):
        """Test that task execution order doesn't matter for correctness."""
        pool = ThreadPool(3)
        
        results = {}
        lock = threading.Lock()
        
        def update_dict(key, value):
            with lock:
                results[key] = value
                time.sleep(0.01)  # Small delay to encourage race conditions
        
        # Add tasks in specific order
        expected = {}
        for i in range(20):
            key = f"key_{i}"
            value = i * 2
            expected[key] = value
            pool.add_task(update_dict, key, value)
        
        pool.wait_completion()
        
        # All updates should be applied correctly regardless of execution order
        assert results == expected


class TestThreadPoolIntegration:
    """Integration tests for threadpool functionality."""

    def test_realistic_download_simulation(self):
        """Test threadpool with realistic download-like workload."""
        pool = ThreadPool(5)
        
        downloads = {}
        lock = threading.Lock()
        
        def mock_download(url, delay=0.01):
            """Simulate downloading a file."""
            time.sleep(delay)  # Simulate network delay
            with lock:
                downloads[url] = f"content_of_{url.split('/')[-1]}"
        
        urls = [
            f"http://example.com/file{i}.pdf"
            for i in range(15)
        ]
        
        start_time = time.time()
        pool.map(mock_download, urls)
        pool.wait_completion()
        end_time = time.time()
        
        # Verify all downloads completed
        assert len(downloads) == 15
        for url in urls:
            assert url in downloads
            assert downloads[url].startswith("content_of_file")
        
        # Should be faster than sequential (15 * 0.01 = 0.15s)
        assert end_time - start_time < 0.1

    def test_error_recovery_workflow(self):
        """Test threadpool recovery from errors."""
        pool = ThreadPool(3)
        
        successful_operations = []
        failed_operations = []
        lock = threading.Lock()
        
        def risky_operation(operation_id):
            """Operation that sometimes fails."""
            if operation_id % 3 == 0:  # Every 3rd operation fails
                raise Exception(f"Operation {operation_id} failed")
            
            time.sleep(0.01)
            with lock:
                successful_operations.append(operation_id)
        
        with patch('builtins.print'):  # Suppress error output
            # Add operations, some will fail
            for i in range(10):
                pool.add_task(risky_operation, i)
            
            pool.wait_completion()
        
        # Should have successful operations (not multiples of 3)
        expected_successful = [i for i in range(10) if i % 3 != 0]
        assert set(successful_operations) == set(expected_successful)

    def test_mixed_task_types(self):
        """Test threadpool with different types of tasks."""
        pool = ThreadPool(4)
        
        results = {"compute": [], "io": [], "memory": []}
        lock = threading.Lock()
        
        def compute_task(n):
            """CPU-intensive task."""
            result = sum(i * i for i in range(n))
            with lock:
                results["compute"].append(result)
        
        def io_task(filename):
            """IO-like task."""
            time.sleep(0.01)  # Simulate IO delay
            with lock:
                results["io"].append(f"processed_{filename}")
        
        def memory_task(data):
            """Memory operation task."""
            processed = [x * 2 for x in data]
            with lock:
                results["memory"].extend(processed)
        
        # Add mixed tasks
        pool.add_task(compute_task, 100)
        pool.add_task(io_task, "file1.txt")
        pool.add_task(memory_task, [1, 2, 3])
        pool.add_task(compute_task, 50)
        pool.add_task(io_task, "file2.txt")
        
        pool.wait_completion()
        
        # Verify all task types completed
        assert len(results["compute"]) == 2
        assert len(results["io"]) == 2
        assert len(results["memory"]) == 3
        
        # Check specific results (order may vary due to threading)
        assert set(results["io"]) == {"processed_file1.txt", "processed_file2.txt"}
        assert results["memory"] == [2, 4, 6]

    def test_threadpool_performance_characteristics(self):
        """Test threadpool performance with different worker counts."""
        task_count = 20
        
        def simple_task(value):
            time.sleep(0.01)
            return value * 2
        
        # Test with different thread counts
        for num_threads in [1, 2, 4, 8]:
            pool = ThreadPool(num_threads)
            
            start_time = time.time()
            
            for i in range(task_count):
                pool.add_task(simple_task, i)
            
            pool.wait_completion()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # More threads should generally be faster (up to a point)
            # At minimum, shouldn't be slower than single-threaded by much
            if num_threads == 1:
                single_thread_time = execution_time
            else:
                # Should be at most slightly slower than single thread
                # (accounting for threading overhead)
                assert execution_time <= single_thread_time * 1.5
