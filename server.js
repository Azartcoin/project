const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 8080;

// Статические файлы
app.use(express.static(path.join(__dirname, 'public')));
app.use('/themes', express.static(path.join(__dirname, 'themes')));
app.use('/css', express.static(path.join(__dirname, 'css')));
app.use('/images', express.static(path.join(__dirname, 'images')));
app.use('/individual_ankets', express.static(path.join(__dirname, 'individual_ankets')));
app.use('/ankets', express.static(path.join(__dirname, 'ankets')));
app.use('/pay', express.static(path.join(__dirname, 'pay')));
// Главная страница
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API для получения списка анкет
app.get('/api/ankety', (req, res) => {
    const generalDirectoryPath = path.join(__dirname, 'public', 'html'); 
    const userId = req.query.userId; 

    fs.readdir(generalDirectoryPath, (err, files) => {
        if (err) {
            return res.status(500).send('Не удалось получить список файлов');
        }

        const htmlFiles = files.filter(file => path.extname(file) === '.html');
        const individualAnkets = userId ? getIndividualAnketsForUser(userId) : [];
        
        res.json([...htmlFiles, ...individualAnkets]);
    });
});

// Функция для получения индивидуальных анкет пользователя
function getIndividualAnketsForUser(userId) {
    const directoryPath = path.join(__dirname, 'individual_ankets');

    const individualAnkets = fs.readdirSync(directoryPath)
        .filter(file => file.startsWith(`${userId}-`) && path.extname(file) === '.html');
    
    return individualAnkets;
}

// Обработчик для индивидуальных анкет по ID
app.get('/:id', (req, res) => {
    const { id } = req.params;
    if (id) {
        res.cookie('userId', id, { maxAge: 30 * 24 * 60 * 60 * 1000, path: '/' }); 
    }
    res.sendFile(path.join(__dirname, 'public', 'index.html')); 
});

// Запуск сервера
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Сервер запущен на http://0.0.0.0:${PORT}`);
});
