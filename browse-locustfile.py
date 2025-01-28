from locust import FastHttpUser, task, events
from contextlib import contextmanager
import time

class OptimizedBrowseUser(FastHttpUser):
    # Define host as a class attribute
    host = "http://localhost:5000"
    
    # Common headers used across all requests
    default_headers = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",
        "Sec-GPC": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Host": "localhost:5000",
        "Priority": "u=0, i",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Upgrade-Insecure-Requests": "1",
    }

    def on_start(self):
        """Initialize session-wide resources."""
        # Pre-set headers for all requests
        self.client.headers.update(self.default_headers)

    @contextmanager
    def timer(self, name):
        """Custom timer context manager for detailed performance monitoring."""
        start_time = time.time()
        try:
            yield
        finally:
            total_time = time.time() - start_time
            events.request.fire(
                request_type="TIMER",
                name=name,
                response_time=total_time * 1000,  # Convert to milliseconds
                response_length=0,
                exception=None,
            )

    @task
    def browse(self):
        """Main browsing task with error handling and performance monitoring."""
        with self.timer("browse_complete_task"):
            try:
                with self.client.get(
                    "/browse",
                    catch_response=True,
                    timeout=30.0  # Explicit timeout
                ) as response:
                    if response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Unexpected status code: {response.status_code}")
            except Exception as e:
                events.request.fire(
                    request_type="GET",
                    name="/browse",
                    response_time=0,
                    response_length=0,
                    exception=e,
                )

if __name__ == "__main__":
    run_single_user(OptimizedBrowseUser)