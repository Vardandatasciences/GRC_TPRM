<template>
  <div class="tprm-wrapper">
    <div v-if="!hasBaseUrl" class="tprm-wrapper__message">
      <p>
        <strong>VUE_APP_TPRM_BASE_URL</strong> is not configured. Set it in your
        <code>.env</code> file to embed the TPRM application.
      </p>
    </div>
    <div v-else class="tprm-wrapper__frame">
      <iframe
        ref="tprmIframe"
        :src="iframeSrc"
        title="TPRM Module"
        frameborder="0"
        referrerpolicy="no-referrer"
        @load="onIframeLoad"
      />
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const BASE_URL = process.env.VUE_APP_TPRM_BASE_URL || ''

export default {
  name: 'TprmWrapper',
  setup() {
    const route = useRoute()
    const tprmIframe = ref(null)

    const normalizedPath = computed(() => {
      const param = route.params.tprmPath

      let pathValue = ''
      if (Array.isArray(param)) {
        pathValue = param.join('/')
      } else if (typeof param === 'string') {
        pathValue = param
      }

      const cleanPath = pathValue ? `/${pathValue}` : '/'
      const query = route.query
      const queryString = new URLSearchParams(query).toString()

      return queryString ? `${cleanPath}?${queryString}` : cleanPath
    })

    const iframeSrc = computed(() => {
      if (!BASE_URL) return ''
      const base = BASE_URL.endsWith('/') ? BASE_URL.slice(0, -1) : BASE_URL
      return `${base}${normalizedPath.value}`
    })

    // Get auth data from GRC localStorage
    const getAuthData = () => {
      const token = localStorage.getItem('access_token') || 
                    localStorage.getItem('session_token') || 
                    localStorage.getItem('token')
      const user = localStorage.getItem('user') || localStorage.getItem('current_user')
      const refreshToken = localStorage.getItem('refresh_token')
      
      return {
        type: 'GRC_AUTH_SYNC',
        token,
        refreshToken,
        user: user ? JSON.parse(user) : null,
        isAuthenticated: localStorage.getItem('isAuthenticated') === 'true' || 
                         localStorage.getItem('is_logged_in') === 'true'
      }
    }

    // Send auth data to TPRM iframe
    const sendAuthToIframe = () => {
      if (tprmIframe.value && tprmIframe.value.contentWindow) {
        const authData = getAuthData()
        console.log('[TprmWrapper] Sending auth data to TPRM iframe:', { 
          hasToken: !!authData.token, 
          hasUser: !!authData.user,
          isAuthenticated: authData.isAuthenticated 
        })
        tprmIframe.value.contentWindow.postMessage(authData, '*')
      }
    }

    const onIframeLoad = () => {
      console.log('[TprmWrapper] TPRM iframe loaded, syncing auth...')
      // Small delay to ensure iframe is ready to receive messages
      setTimeout(sendAuthToIframe, 100)
    }

    // Listen for auth requests from TPRM iframe
    const handleMessage = (event) => {
      // Verify origin if BASE_URL is configured
      if (BASE_URL) {
        const baseOrigin = new URL(BASE_URL).origin
        if (event.origin !== baseOrigin && event.origin !== window.location.origin) {
          return
        }
      }

      if (event.data && event.data.type === 'TPRM_AUTH_REQUEST') {
        console.log('[TprmWrapper] Received auth request from TPRM')
        sendAuthToIframe()
      }
    }

    onMounted(() => {
      window.addEventListener('message', handleMessage)
    })

    onUnmounted(() => {
      window.removeEventListener('message', handleMessage)
    })

    return {
      tprmIframe,
      iframeSrc,
      hasBaseUrl: computed(() => Boolean(BASE_URL)),
      onIframeLoad
    }
  }
}
</script>

<style scoped>
.tprm-wrapper {
  width: 100%;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  background: #f5f6fb;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e3e7f0;
}

.tprm-wrapper__frame {
  flex: 1;
  position: relative;
}

.tprm-wrapper__frame iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
  background: white;
}

.tprm-wrapper__message {
  padding: 32px;
  text-align: center;
  color: #0f172a;
}

.tprm-wrapper__message code {
  background: #e2e8f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}
</style>

