// Скрипт для добавления API ключей в localStorage
// Запустите это в консоли браузера на странице Morphik

// Добавляем конфигурацию API ключей
const apiKeys = {
  anthropic: {
    apiKey: "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"
  },
  openai: {
    apiKey: "***"  // Добавьте ваш ключ если есть
  },
  google: {
    apiKey: "***"  // Добавьте ваш ключ если есть
  }
};

// Сохраняем в localStorage
localStorage.setItem('morphik_api_keys', JSON.stringify(apiKeys));

console.log('API keys добавлены в localStorage!');
console.log('Обновите страницу чтобы увидеть модели');