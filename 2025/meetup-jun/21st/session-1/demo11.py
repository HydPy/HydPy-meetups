def consumer():
    print("[Consumer] Ready")
    while True:
        item = yield
        print(f"[Consumer] Got item: {item}")

def producer(c):
    print("[Producer] Starting...")
    next(c)  # Prime the consumer (advance to first yield)
    for i in range(5):
        print(f"[Producer] Sending: {i}")
        c.send(i)
        yield  # Yield control back to scheduler

def run_scheduler(*coroutines):
    coroutines = [coroutine for coroutine in coroutines] # Better way?
    while coroutines:
        for coro in coroutines[:]:
            try:
                next(coro)
            except StopIteration:
                coroutines.remove(coro)


if __name__ == "__main__":
    # generator based coroutine.
    c = consumer()
    p = producer(c)
    run_scheduler(p)
