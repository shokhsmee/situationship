import { createI18n } from 'vue-i18n'
import en from './en'
import ru from './ru'
import uz from './uz'

const saved = localStorage.getItem('situationship_locale')

export const i18n = createI18n({
  legacy: false,
  locale: saved || 'en',
  fallbackLocale: 'en',
  messages: { en, ru, uz },
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('situationship_locale', locale)
}
