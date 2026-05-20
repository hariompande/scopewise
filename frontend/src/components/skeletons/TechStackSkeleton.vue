<template>
  <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
    <div v-for="i in 6" :key="i" class="p-3 rounded-md animate-pulse skeleton-card">
      <div class="h-3 skeleton-bg rounded w-16 mb-2"></div>
      <div class="h-4 skeleton-bg-strong rounded w-20"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-card {
  background: rgba(0, 0, 0, 0.2);
}

.skeleton-bg {
  background: rgba(255, 255, 255, 0.1);
}

.skeleton-bg-strong {
  background: rgba(255, 255, 255, 0.2);
}
</style>
