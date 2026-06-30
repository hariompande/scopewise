FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install -U uv

# Copy the project files
COPY . .

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
