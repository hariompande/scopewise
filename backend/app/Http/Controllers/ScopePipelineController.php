<?php

namespace App\Http\Controllers;

use App\Http\Requests\PipelineRunRequest;
use App\Services\PythonService;
use GuzzleHttp\Client;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ScopePipelineController extends Controller
{
    protected PythonService $pythonService;

    public function __construct(PythonService $pythonService)
    {
        $this->pythonService = $pythonService;
    }

    /**
     * Run the scope analysis pipeline (blocking)
     *
     * @param PipelineRunRequest $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function run(PipelineRunRequest $request)
    {
        try {
            $result = $this->pythonService->runPipeline($request->validated('user_input'));
            return response()->json($result);
        } catch (\RuntimeException $e) {
            return response()->json(['error' => $e->getMessage()], 502);
        }
    }

    /**
     * Run the scope analysis pipeline with SSE streaming
     *
     * @param PipelineRunRequest $request
     * @return StreamedResponse
     */
    public function runStream(PipelineRunRequest $request)
    {
        $pythonUrl = config('services.python_service.url', env('PYTHON_SERVICE_URL', 'http://localhost:8000'));
        $userInput = $request->validated('user_input');

        return new StreamedResponse(function () use ($pythonUrl, $userInput) {
            // Disable output buffering
            if (ob_get_level()) {
                ob_end_clean();
            }
            ini_set('output_buffering', '0');
            ini_set('zlib.output_compression', '0');

            $client = new Client(['timeout' => 300]);
            $response = $client->post($pythonUrl . '/api/pipeline/run-stream', [
                'json' => ['user_input' => $userInput],
                'headers' => [
                    'Accept' => 'text/event-stream',
                ],
                'stream' => true,
            ]);

            $body = $response->getBody();
            while (!$body->eof()) {
                $data = $body->read(1024);
                echo $data;
                if (ob_get_level()) {
                    ob_flush();
                }
                flush();
            }
        }, Response::HTTP_OK, [
            'Content-Type' => 'text/event-stream',
            'Cache-Control' => 'no-cache',
            'Connection' => 'keep-alive',
            'X-Accel-Buffering' => 'no',
        ]);
    }

    /**
     * Stream pipeline status by request ID
     *
     * @param string $requestId
     * @return StreamedResponse
     */
    public function streamStatus(string $requestId)
    {
        $pythonUrl = config('services.python_service.url', env('PYTHON_SERVICE_URL', 'http://localhost:8000'));

        return new StreamedResponse(function () use ($pythonUrl, $requestId) {
            // Disable output buffering
            if (ob_get_level()) {
                ob_end_clean();
            }
            ini_set('output_buffering', '0');
            ini_set('zlib.output_compression', '0');

            $client = new Client(['timeout' => 300]);
            $response = $client->get($pythonUrl . '/api/pipeline/stream/' . $requestId, [
                'headers' => [
                    'Accept' => 'text/event-stream',
                ],
                'stream' => true,
            ]);

            $body = $response->getBody();
            while (!$body->eof()) {
                $data = $body->read(1024);
                echo $data;
                if (ob_get_level()) {
                    ob_flush();
                }
                flush();
            }
        }, Response::HTTP_OK, [
            'Content-Type' => 'text/event-stream',
            'Cache-Control' => 'no-cache',
            'Connection' => 'keep-alive',
            'X-Accel-Buffering' => 'no',
        ]);
    }

    /**
     * Health check for the Python service
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function health()
    {
        $isHealthy = $this->pythonService->healthCheck();
        return response()->json(['status' => $isHealthy ? 'ok' : 'error']);
    }
}
