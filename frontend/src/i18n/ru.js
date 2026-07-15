export default {
  app: { title: 'Situationship', tagline: 'Каждая улика — признание.' },
  auth: {
    login: 'Войти', register: 'Регистрация', logout: 'Выйти',
    username: 'Имя пользователя', password: 'Пароль', displayName: 'Отображаемое имя',
    guest: 'Играть гостем',
  },
  home: {
    create: 'Создать игру', join: 'Присоединиться', code: 'Код комнаты',
    browse: 'Выберите дело', admin: 'Студия',
  },
  lobby: {
    title: 'Лобби', players: 'Игроки', waiting: 'Ждём, пока хост начнёт…',
    start: 'Начать расследование', share: 'Поделиться кодом', host: 'Хост',
    needMore: 'Нужно минимум {n} следователей',
  },
  phases: {
    lobby: 'Лобби', intro: 'Брифинг', evidence: 'Улики', discussion: 'Обсуждение',
    event: 'Событие', vote: 'Финальный ответ', insider_guess: 'Раскрыть инсайдера', result: 'Вердикт',
  },
  game: {
    yourRole: 'Ваша роль', yourHand: 'Ваши улики', board: 'Доска улик',
    reveal: 'Раскрыть', revealed: 'Раскрыто', locked: 'Заблокировано', map: 'Карта города',
    insiderGoal: 'Тайная цель', submitVote: 'Отправить ответ', voteFor: 'Обвинить это место',
    guessInsider: 'Кто инсайдер?', skip: 'Пропустить', advance: 'Следующая фаза',
  },
  result: {
    investigatorsWin: 'Победа следователей', insiderWin: 'Победа инсайдера',
    truth: 'Что произошло на самом деле', insiderWas: 'Инсайдером был', caught: 'Разоблачён!',
    escaped: 'Ушёл от разоблачения', scoreboard: 'Таблица очков', playAgain: 'Играть снова',
  },
  common: { loading: 'Загрузка…', error: 'Что-то пошло не так', back: 'Назад', save: 'Сохранить' },
}
