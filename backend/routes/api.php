<?php

use App\Http\Controllers\ScopePipelineController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::get('/health', [ScopePipelineController::class, 'health']);

Route::prefix('pipeline')->group(function () {
    Route::post('/run', [ScopePipelineController::class, 'run']);
    Route::post('/run-stream', [ScopePipelineController::class, 'runStream']);
    Route::get('/stream/{requestId}', [ScopePipelineController::class, 'streamStatus']);
});
