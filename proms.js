async function getClientData(id) {

    const user = {
        id: id,
        name: "Ivan",
        role: "admin"
    };

    return user;
}

function processData() {

    getClientData(1)
        .then(result => {
            // Запихиваем данные в переменную
            let myData = result; 
            
            // РАБОТАЕМ С НЕЙ ТОЛЬКО ТУТ
            console.log("Данные внутри переменной:", myData);
            return transformData(myData); // Можно передать в следующую функцию
        })
        // данные из последнего then передаются сюда
        .then(transformed => {
            console.log("Результат обработки:", transformed);
        })
        .catch(err => console.error("Ошибка:", err));
}

async function sendClientData() {
    const data = await getClientData(1);

    return data
}


import { parentPort, workerData } from 'worker_threads';

// Тяжелая функция (CPU-intensive)
const doWork = (limit) => {
    let sum = 0;
    for (let i = 0; i < limit; i++) {
        sum += i;
    }
    return sum;
};
const result = doWork(workerData.iterations);

parentPort.postMessage(result);


console.log("1"); // (А) Синхронный код

setTimeout(() => {
    console.log("2"); // (Б) Макрозадача
}, 0);

Promise.resolve().then(() => {
    console.log("3"); // (В) Микрозадача
});

console.log("4"); // (Г) Синхронный код