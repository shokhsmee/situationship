export default {
  app: { title: 'Situationship', tagline: 'Every clue is a confession.' },
  auth: {
    login: 'Log in', register: 'Register', logout: 'Log out',
    username: 'Username', password: 'Password', displayName: 'Display name',
    guest: 'Play as guest',
  },
  home: {
    create: 'Create game', join: 'Join game', code: 'Room code',
    browse: 'Choose a case', admin: 'Studio',
  },
  lobby: {
    title: 'Lobby', players: 'Players', waiting: 'Waiting for the host to begin…',
    start: 'Start investigation', share: 'Share code', host: 'Host',
    needMore: 'Need at least {n} investigators',
  },
  phases: {
    lobby: 'Lobby', intro: 'Briefing', evidence: 'Evidence', discussion: 'Discussion',
    event: 'Development', vote: 'Final answer', insider_guess: 'Unmask the insider', result: 'Verdict',
  },
  game: {
    yourRole: 'Your role', yourHand: 'Your evidence', board: 'Evidence board',
    reveal: 'Reveal', revealed: 'Revealed', locked: 'Locked', map: 'City map',
    insiderGoal: 'Secret objective', submitVote: 'Submit answer', voteFor: 'Accuse this place',
    guessInsider: 'Who is the insider?', skip: 'Skip', advance: 'Advance phase',
  },
  result: {
    investigatorsWin: 'Investigators win', insiderWin: 'The insider wins',
    truth: 'What really happened', insiderWas: 'The insider was', caught: 'Unmasked!',
    escaped: 'Escaped detection', scoreboard: 'Scoreboard', playAgain: 'Play again',
  },
  common: { loading: 'Loading…', error: 'Something went wrong', back: 'Back', save: 'Save' },
}
