<!DOCTYPE html>
<html lang="ru">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/styles/resultsinmatch_style.css">
    <title>QUIZAI</title>
</head>

<body>
<div class="main_cont">
    <header>
        <a href="main.html" class="btn_back" id="back-btn">НАЗАД</a>
        <h1 class="h11">QUIZ AI ARENA</h1>
    </header>

    <p class="h12">РЕЗУЛЬТАТЫ:</p>

    <main>
        <div class="raiting" id="results-container">
            <div class="tablehead">
                <span>МЕСТО</span>
                <span>ИМЯ ПОЛЬЗОВАТЕЛЯ</span>
                <span>СЧЁТ</span>
            </div>
            <!-- Результаты будут загружены через JavaScript -->
        </div>
    </main>
</div>
</body>

<script src="/js/auth.js"></script>
<script src="/js/checkCurrentGame.js"></script>
<script>
    let gameId = null;
    let gameStopped = false;

    document.addEventListener('DOMContentLoaded', function () {
      if (!AuthService.requireAuth()) return;

      // Получаем gameId из URL параметров
      const urlParams = new URLSearchParams(window.location.search);
      gameId = urlParams.get('gameId');

      if (!gameId) {
        console.error('Game ID не найден в URL');
        return;
      }

      // Загружаем результаты
      loadResults();

      // Обработчик для кнопки "Назад"
      document.getElementById('back-btn').addEventListener('click', function(e) {
        e.preventDefault();
        stopGameAndRedirect('main.html');
      });

      // Обработчик для закрытия/перехода со страницы
      window.addEventListener('beforeunload', function() {
        if (!gameStopped) {
          stopGame();
        }
      });
    });

    async function stopGameAndRedirect(redirectUrl) {
      await stopGame();
      window.location.href = redirectUrl;
    }

    async function stopGame() {
      if (gameStopped) return; // Не останавливать игру повторно

      try {
        const session = AuthService.getsession();

        const response = await fetch('http://localhost:8080/api/game/stop', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + session,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            gameId: parseInt(gameId)
          })
        });

**Логика работы:**
1. Конструктор дескриптора `__init__` должен принимать функцию или метод, результат которой нужно кэшировать.
2. При обращении к атрибуту (через метод `__get__`), дескриптор должен:
    *   Проверить, есть ли значение в кэше (объект кэша можно брать из самого экземпляра класса, например, через `instance.cache`).
    *   Если значение в кэше есть — вернуть его.
    *   Если значения нет — вызвать сохраненную функцию, передав ей `instance`, сохранить результат в кэш и вернуть его.

        localStorage.removeItem('currentGameId');
        localStorage.removeItem('selectedTopic');
        gameStopped = true;

        console.log('Игра успешно остановлена');

      } catch (error) {
        console.error('Ошибка остановки игры:', error);
      }
    }

    async function stopGameAndRedirect(redirectUrl) {
      await stopGame();
      window.location.href = redirectUrl;
    }

    async function stopGame() {
      if (gameStopped) return;

```python

class HeavyCalculator:
    def __init__(self, cache):
        self.cache = cache

    def compute_sum(self):
        print("Сложные вычисления...")
        return sum(range(10**6))

    # Прямое присваивание дескриптора атрибуту класса
    # Теперь при обращении к calculator.big_data будет срабатывать логика кэширования
    big_data = CachedProperty(compute_sum)

cache = Cache(storage=DictStorage(), policy=LFUPolicy(capacity=10))
calculator = HeavyCalculator(cache)

print(calculator.big_data) # Сработают вычисления
print(calculator.big_data) # Значение возьмется из кэша
```

---

        const response = await fetch('http://localhost:8080/api/game/stop', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + session,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            gameId: parseInt(gameId)
          })
        });

        if (!response.ok) {
          throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        localStorage.removeItem('currentGameId');
        localStorage.removeItem('selectedTopic');
        gameStopped = true;

        console.log('Игра успешно остановлена');

      } catch (error) {
        console.error('Ошибка остановки игры:', error);
      }
    }

    async function loadResults() {
      try {
        const session = AuthService.getsession();

        console.log('Загрузка результатов для игры:', gameId);

        const response = await fetch('http://localhost:8080/api/leaderboard/get/by-game', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + session,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            gameId: parseInt(gameId)
          })
        });

        if (!response.ok) {
          throw new Error(`Ошибка HTTP: ${response.status}`);
        }

        const resultsText = await response.text();
        console.log('Ответ сервера:', resultsText);

        // Парсим JSON строку в массив
        const resultsArray = JSON.parse(resultsText);
        console.log('Парсинг результатов:', resultsArray);

        // Преобразуем массив массивов в массив объектов
        const results = resultsArray.map(item => ({
          username: item[0] || 'Неизвестный игрок',
          score: item[1] || 0
        }));

        console.log('Преобразованные результаты:', results);

        // Отображаем результаты
        displayResults(results);

      } catch (error) {
        console.error('Ошибка загрузки результатов:', error);
        displayError('Ошибка загрузки результатов: ' + error.message);
      }
    }

    function displayResults(results) {
      const container = document.getElementById('results-container');

      // Очищаем контейнер, оставляя только заголовок
      const tableHead = container.querySelector('.tablehead');
      container.innerHTML = '';
      container.appendChild(tableHead);

      if (!results || results.length === 0) {
        container.innerHTML += '<div class="no-results">Результаты пока недоступны</div>';
        return;
      }

      // Сортируем результаты по убыванию счета
      const sortedResults = [...results].sort((a, b) => b.score - a.score);

      // Создаем элементы для каждого игрока
      sortedResults.forEach((player, index) => {
        const playerElement = createPlayerElement(player, index + 1);
        container.appendChild(playerElement);
      });

      console.log(`Отображено ${sortedResults.length} результатов`);
    }

    function createPlayerElement(player, position) {
      const playerDiv = document.createElement('div');
      playerDiv.className = 'player';

      const textDiv = document.createElement('div');
      textDiv.className = 'text';

      // Место
      const positionElement = document.createElement('p');
      positionElement.className = 'h13';
      positionElement.textContent = position;

      // Имя пользователя
      const usernameElement = document.createElement('p');
      usernameElement.className = 'h13';
      usernameElement.textContent = player.username;

      // Счет
      const scoreElement = document.createElement('p');
      scoreElement.className = 'h13';
      scoreElement.textContent = player.score;

      textDiv.appendChild(positionElement);
      textDiv.appendChild(usernameElement);
      textDiv.appendChild(scoreElement);
      playerDiv.appendChild(textDiv);
      return playerDiv;
    }

    function displayError(message) {
      const container = document.getElementById('results-container');
      const tableHead = container.querySelector('.tablehead');
      container.innerHTML = '';
      container.appendChild(tableHead);

      const errorElement = document.createElement('div');
      errorElement.className = 'no-results';
      errorElement.textContent = message;
      container.appendChild(errorElement);
    }

    // Добавляем CSS для сообщения об ошибке/отсутствии результатов
    const style = document.createElement('style');
    style.textContent = `
        .no-results {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100%;
          height: 200px;
          font-size: 1.5rem;
          color: #666;
          text-align: center;
        }
      `;
    document.head.appendChild(style);
</script>

</html>