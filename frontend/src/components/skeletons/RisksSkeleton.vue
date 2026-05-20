<template>
  <div class="space-y-2">
    <div v-for="i in 3" :key="i" class="p-3 rounded-md animate-pulse skeleton-card">
      <div class="h-4 skeleton-bg rounded w-3/4 mb-2"></div>
      <div class="h-3 skeleton-bg rounded w-1/2"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-card {
  background: rgba(255, 107, 107, 0.1);
}

.skeleton-bg {
  background: rgba(255, 255, 255, 0.15);
}
</style>
