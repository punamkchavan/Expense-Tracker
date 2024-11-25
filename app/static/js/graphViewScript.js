const divAlert = document.getElementById('div-alert');
const GraphDiv = document.getElementById('GraphDiv');
const HeadingDiv = document.getElementById('HeadingDiv');
const btnShowExpenseGraph = document.getElementById('btnShowExpenseGraph');
const btnShowIncomeGraph = document.getElementById('btnShowIncomeGraph');
const btnShowSavingsGriph = document.getElementById('btnShowSavingsGriph');

document.addEventListener('DOMContentLoaded', fetchData('Expense'));
async function fetchData(Type) {
    if (Type == 'Savings') {
        try {
            const result = await axios.get('/expense/getSavingsData/');

            const currentYear = new Date().getFullYear().toString();
            const monthlyData = result.data.filter(item => {
                const [month, year] = item.year.split('-');
                return year === currentYear;
            });

            const resultArray = formatSavingsData(monthlyData);
            displayGraph(resultArray, Type);

        } catch (error) {
            console.log(error);
        }
    }
    else {
        try {
            const result = await axios.get('/expense/viewReportExpensesData/');
            const thisMonthStart = moment().startOf('month');
            console.log(result);
            const monthlyData = result.data.filter(item => {
                const itemDate = moment(item.date, 'DD/MM/YYYY');
                return itemDate.isSameOrAfter(thisMonthStart, 'day');
            });

            const resultArray = formatData(monthlyData, Type)
            displayGraph(resultArray, Type);

        } catch (error) {
            await displayNotification("Internal Server Error!", 'danger', divAlert);
        }
    }
}

function formatData(data, Type) {
    const sumBySourceType = {};

    data.forEach(item => {
        const { amount, source_type, type } = item;
        const Amount = parseInt(amount);
        if (type === Type) {
            if (sumBySourceType[source_type]) {
                sumBySourceType[source_type] += Amount;
            } else {
                sumBySourceType[source_type] = Amount;
            }
        }
    });

    const resultArray = Object.entries(sumBySourceType).map(([source_type, sum]) => {
        return { source_type, amount: sum.toString() };
    });
    return resultArray
}
function formatSavingsData(data) {
    const resultArray = data.map(item => ({
        month: moment(item.year, 'MM-YYYY').format('MMMM'),
        savings: parseInt(item.savings),
    }));
    return resultArray;
}

if (btnShowExpenseGraph) {
    btnShowExpenseGraph.addEventListener("click", function () {
        fetchData("Expense")
    });
}

if (btnShowIncomeGraph) {
    btnShowIncomeGraph.addEventListener("click", function () {
        fetchData("Income");
    });
}
if (btnShowSavingsGriph) {
    btnShowSavingsGriph.addEventListener('click', function () {
        fetchData('Savings');
    });
}

function displayGraph(data, type) {
    console.log(data);
    let labels;
    let amounts;
    let notation = '';
    if (type == 'Savings') {
        labels = data.map(item => item.month);
        amounts = data.map(item => item.savings);
        notation = 'Year'
    } else {
        labels = data.map(item => item.source_type);
        amounts = data.map(item => parseInt(item.amount));
        notation = 'Month'
    }
    const ctx = document.createElement('canvas');
    HeadingDiv.innerHTML = '';
    GraphDiv.innerHTML = '';
    HeadingDiv.className = 'text-center mt-5 mb-3';
    HeadingDiv.innerHTML = `<h5>${type} Graph of Current ${notation}</h5>`;
    GraphDiv.appendChild(ctx);

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: amounts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: true,
                position: 'bottom',
                labels: {
                    fontColor: 'black',
                    fontSize: 14,
                    padding: 10
                }
            },
            plugins: {
                datalabels: {
                    color: 'white',
                    formatter: (value, context) => {
                        return context.chart.data.labels[context.dataIndex] + '\n' + value;
                    }
                }
            },
            elements: {
                arc: {
                    borderWidth: 2
                }
            }
        }
    });
}
function displayNotification(message, type, container) {
    return new Promise((resolve) => {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `alert alert-${type}`;
        notificationDiv.textContent = message;
        container.appendChild(notificationDiv);
        setTimeout(() => {
            notificationDiv.remove();
            resolve();
        }, 2000);
    });
}



