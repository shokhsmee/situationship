<script setup>
import { onMounted } from 'vue'
import { RouterView, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTelegram } from '@/composables/useTelegram'
import ToastHost from '@/components/shared/ToastHost.vue'
import LocaleSwitcher from '@/components/shared/LocaleSwitcher.vue'
import EventPopup from '@/components/game/EventPopup.vue'

const auth = useAuthStore()
const { ready, isTelegram } = useTelegram()

onMounted(() => {
  if (isTelegram.value) ready()
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="flex items-center justify-between px-4 py-3 border-b border-noir-800">
      <RouterLink to="/" class="font-display text-lg tracking-wide text-amber-glow">
        🔍 {{ $t('app.title') }}
      </RouterLink>
      <div class="flex items-center gap-3">
        <LocaleSwitcher />
        <RouterLink
          v-if="auth.isWriter"
          to="/admin"
          class="text-xs text-evidence/60 hover:text-amber-glow"
        >
          {{ $t('home.admin') }}
        </RouterLink>
        <button
          v-if="auth.isAuthenticated"
          class="text-xs text-evidence/60 hover:text-red-400"
          @click="auth.logout()"
        >
          {{ $t('auth.logout') }}
        </button>
      </div>
    </header>

    <main class="flex-1 relative">
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <EventPopup />
    <ToastHost />
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
