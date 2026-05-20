<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;

class PythonService
{
    protected string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = config('services.python_service.url', env('PYTHON_SERVICE_URL', 'http://localhost:8000'));
    }

    /**
     * Run the scope analysis pipeline (blocking)
     *
     * @param string $userInput
     * @return array
     */
    public function runPipeline(string $userInput): array
    {
        $response = Http::timeout(300)->post("{$this->baseUrl}/api/pipeline/run", [
            'user_input' => $userInput,
        ]);

        if ($response->failed()) {
            throw new \RuntimeException("Python service error: {$response->body()}");
        }

        return $response->json();
    }

    /**
     * Run the scope analysis pipeline with streaming
     *
     * @param string $userInput
     * @return \Illuminate\Http\Client\Response
     */
    public function runPipelineStream(string $userInput)
    {
        return Http::timeout(300)
            ->withHeaders([
                'Accept' => 'text/event-stream',
                'Cache-Control' => 'no-cache',
            ])
            ->post("{$this->baseUrl}/api/pipeline/run-stream", [
                'user_input' => $userInput,
            ]);
    }

    /**
     * Stream pipeline status by request ID
     *
     * @param string $requestId
     * @return \Illuminate\Http\Client\Response
     */
    public function streamPipelineStatus(string $requestId)
    {
        return Http::timeout(300)
            ->withHeaders([
                'Accept' => 'text/event-stream',
                'Cache-Control' => 'no-cache',
            ])
            ->get("{$this->baseUrl}/api/pipeline/stream/{$requestId}");
    }

    /**
     * Check if the Python service is healthy
     *
     * @return bool
     */
    public function healthCheck(): bool
    {
        try {
            $response = Http::timeout(5)->get("{$this->baseUrl}/health");
            return $response->successful();
        } catch (\Exception $e) {
            return false;
        }
    }
}
