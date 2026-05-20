<template>
  <div class="space-y-3">
    <div v-for="i in 3" :key="i" class="p-3 rounded-md animate-pulse skeleton-card">
      <div class="flex justify-between items-start mb-2">
        <div class="h-5 skeleton-bg rounded w-32"></div>
        <div class="h-4 skeleton-bg rounded w-16"></div>
      </div>
      <div class="h-3 skeleton-bg rounded w-2/3"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.skeleton-bg {
  background: rgba(255, 255, 255, 0.15);
}
</style>
