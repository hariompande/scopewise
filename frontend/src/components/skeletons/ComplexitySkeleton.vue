<template>
  <div class="skeleton-container rounded-md p-4">
    <div class="h-6 skeleton-bg rounded w-48 mb-4 animate-pulse"></div>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <div class="h-4 skeleton-bg rounded w-24 mb-2 animate-pulse"></div>
        <div class="h-5 skeleton-bg-strong rounded w-20 animate-pulse"></div>
      </div>
      <div>
        <div class="h-4 skeleton-bg rounded w-20 mb-2 animate-pulse"></div>
        <div class="h-5 skeleton-bg-strong rounded w-32 animate-pulse"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-container {
  background: rgba(0, 0, 0, 0.2);
}

.skeleton-bg {
  background: rgba(255, 255, 255, 0.15);
}

.skeleton-bg-strong {
  background: rgba(255, 255, 255, 0.25);
}
</style>
