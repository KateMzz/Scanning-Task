
## Setup

1. Create a `user_creds.py` file in the `app/scraper_logic/` directory.

    ```python
    # app/scraper_logic/user_creds.py

    user_data = [
        {
            "Username": "",
            "Password": "",
            "Secret_answer": ""
        },
        {
            "Username": "",
            "Password": "",
            "Secret_answer": ""
        },
        {
            "Username": "",
            "Password": "",
            "Secret_answer": ""
        }
    ]
    ```

2. Build the Docker container.

    ```bash
    docker build -t your_image_name .
    ```

3. Run the Docker container.

    ```bash
    docker run your_image_name
    ```

Replace `your_image_name` with the actual name you want to give to your Docker image.
