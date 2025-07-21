# flows/hello.py
from prefect import flow

@flow(log_prints=True)
def hello(name: str = "Prefect 3"):
    print(f"Hola, {name}!")

if __name__ == "__main__":
    # opción Python SDK (útil en CI o para guardar la spec en git)
    hello.deploy(
        name="hello-dev",
        work_pool_name="dev-pool",
        entrypoint="flows/hello.py:hello",
        path=".",                 # carpeta ya montada como /flows
    )
