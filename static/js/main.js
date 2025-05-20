document.addEventListener('DOMContentLoaded', function() {
    // Инициализация параметров
    const parameters = {
        'population': { 
            slider: document.getElementById('populationSlider'), 
            label: document.getElementById('populationLabel'), 
            format: formatPopulation,
            min: 1000000,
            max: 9990000
        },
        'time': { 
            slider: document.getElementById('timeSlider'), 
            label: document.getElementById('timeLabel'), 
            format: formatNumber,
            min: 180,
            max: 1800
        },
        'S': { 
            slider: document.getElementById('SSlider'), 
            label: document.getElementById('SLabel'), 
            format: formatPopulation,
            min: 1000000,
            max: 9990000
        },
        'E': { 
            slider: document.getElementById('ESlider'), 
            label: document.getElementById('ELabel'), 
            format: formatNumber,
            min: 0,
            max: 1000
        },
        'I': { 
            slider: document.getElementById('ISlider'), 
            label: document.getElementById('ILabel'), 
            format: formatNumber,
            min: 1,
            max: 1000
        },
        'R': { 
            slider: document.getElementById('RSlider'), 
            label: document.getElementById('RLabel'), 
            format: formatNumber,
            min: 0,
            max: 1000
        },
        'D': { 
            slider: document.getElementById('DSlider'), 
            label: document.getElementById('DLabel'), 
            format: formatNumber,
            min: 0,
            max: 1000
        },
        'R0': { 
            slider: document.getElementById('R0Slider'), 
            label: document.getElementById('R0Label'), 
            format: formatDecimal,
            min: 1.4,
            max: 5.7
        },
        'gamma': { 
            slider: document.getElementById('gammaSlider'), 
            label: document.getElementById('gammaLabel'), 
            format: formatNumber,
            min: 4,
            max: 18
        },
        'sigma': { 
            slider: document.getElementById('sigmaSlider'), 
            label: document.getElementById('sigmaLabel'), 
            format: formatNumber,
            min: 2,
            max: 14
        },
        'mu': { 
            slider: document.getElementById('muSlider'), 
            label: document.getElementById('muLabel'), 
            format: formatDecimal,
            min: 0.1,
            max: 3.0
        }
    };
    
    // Обработчики событий для всех слайдеров
    Object.keys(parameters).forEach(key => {
        const param = parameters[key];
        
        // Инициализация прогресс-баров
        updateSliderProgress(param.slider);
        
        // Обработка изменений слайдера
        param.slider.addEventListener('input', function(e) {
            const value = e.target.value;
            param.label.textContent = param.format(value);
            updateSliderProgress(e.target);
            
            // Визуальный эффект при изменении значения
            param.label.classList.add('changing');
            setTimeout(() => {
                param.label.classList.remove('changing');
            }, 300);
            
            // Визуальное выделение активного параметра
            const paramCard = e.target.closest('.parameter-card');
            paramCard.classList.add('active');
            setTimeout(() => {
                paramCard.classList.remove('active');
            }, 1000);
            
            // Обновляем график с небольшой задержкой для производительности
            debounceUpdateChart();
        });
    });
    
    // Обработчики для переключения моделей
    const modelTabs = document.querySelectorAll('.model-tab input');
    modelTabs.forEach(tab => {
        tab.addEventListener('change', function() {
            updateModelAvailability();
            updateLegendVisibility();
            updateChart();
            updateModelSummary();
        });
    });
    
    // Функция обновления прогресс-бара слайдера
    function updateSliderProgress(slider) {
        const min = parseFloat(slider.min);
        const max = parseFloat(slider.max);
        const value = parseFloat(slider.value);
        const percentage = ((value - min) / (max - min)) * 100;
        
        const progressBar = slider.previousElementSibling.querySelector('.slider-progress');
        progressBar.style.width = `${percentage}%`;
    }
    
    // Функция для форматирования больших чисел популяции
    function formatPopulation(value) {
        value = parseFloat(value);
        if (value >= 1000000) {
            return (value / 1000000).toFixed(value % 1000000 === 0 ? 0 : 2) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(value % 1000 === 0 ? 0 : 1) + 'K';
        }
        return value.toString();
    }
    
    // Функция для форматирования целых чисел
    function formatNumber(value) {
        return parseInt(value).toString();
    }
    
    // Функция для форматирования десятичных чисел
    function formatDecimal(value) {
        return parseFloat(value).toFixed(2);
    }
    
    // Функция для обновления доступности параметров в зависимости от модели
    function updateModelAvailability() {
        const selectedModel = getSelectedModel();
        const paramCards = document.querySelectorAll('.parameter-card');
        
        // Настройка доступности параметров
        paramCards.forEach(card => {
            const paramName = card.dataset.param;
            
            if (paramName === 'E' || paramName === 'sigma') {
                const isDisabled = selectedModel === 'SIR';
                card.classList.toggle('disabled', isDisabled);
                parameters[paramName].slider.disabled = isDisabled;
            }
            
            if (paramName === 'D' || paramName === 'mu') {
                const isDisabled = selectedModel !== 'SEIRD';
                card.classList.toggle('disabled', isDisabled);
                parameters[paramName].slider.disabled = isDisabled;
            }
        });
    }
    
    // Функция для обновления видимости элементов легенды
    function updateLegendVisibility() {
        const selectedModel = getSelectedModel();
        const legendItems = document.querySelectorAll('.legend-item');
        
        legendItems.forEach(item => {
            const component = item.dataset.component;
            
            if (component === 'E') {
                item.style.display = selectedModel === 'SIR' ? 'none' : 'flex';
            }
            
            if (component === 'D') {
                item.style.display = selectedModel === 'SEIRD' ? 'flex' : 'none';
            }
        });
    }
    
    // Функция получения выбранной модели
    function getSelectedModel() {
        const checkedTab = document.querySelector('.model-tab input:checked');
        return checkedTab ? checkedTab.value : 'SIR';
    }
    
    // Функция для более эффективного обновления графика с debounce
    let updateChartTimeout;
    function debounceUpdateChart() {
        clearTimeout(updateChartTimeout);
        updateChartTimeout = setTimeout(updateChart, 300);
    }
    
    // Функция для обновления графика
    function updateChart() {
        const selectedModel = getSelectedModel();
        const chartContainer = document.getElementById('plotDiv');
        
        // Показываем спиннер загрузки
        chartContainer.innerHTML = '<div class="loading-spinner"></div>';
        
        // Собираем данные из слайдеров
        const formData = {
            'model': selectedModel,
            'population': parseFloat(parameters['population'].slider.value),
            'time': parseInt(parameters['time'].slider.value),
            'S': parseFloat(parameters['S'].slider.value),
            'E': parseFloat(parameters['E'].slider.value),
            'I': parseFloat(parameters['I'].slider.value),
            'R': parseFloat(parameters['R'].slider.value),
            'D': parseFloat(parameters['D'].slider.value),
            'R0': parseFloat(parameters['R0'].slider.value),
            'gamma': 1/parseFloat(parameters['gamma'].slider.value),
            'sigma': 1/parseFloat(parameters['sigma'].slider.value),
            'mu': parseFloat(parameters['mu'].slider.value) / 1000
        };
        
        // Отправляем запрос на сервер
        fetch('/update_plot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            renderChart(data, selectedModel);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            chartContainer.innerHTML = '<div class="error-message">Произошла ошибка при загрузке данных</div>';
        });
    }
    
    // Функция для отрисовки графика
    function renderChart(data, model) {
        const colors = {
            S: 'var(--color-s)',  // синий
            E: 'var(--color-e)',  // оранжевый
            I: 'var(--color-i)',  // красный
            R: 'var(--color-r)',  // зеленый
            D: 'var(--color-d)'   // фиолетовый
        };
        
        const traces = [];
        
        // Компоненты модели S, I, R присутствуют во всех моделях
        traces.push({
            x: data.time,
            y: data.S,
            name: 'Восприимчивые (S)',
            line: { 
                color: colors.S, 
                width: 3,
                shape: 'spline',
                smoothing: 1.3
            },
            type: 'scatter'
        });
        
        // Компонент E присутствует в SEIR и SEIRD моделях
        if (model !== 'SIR') {
            traces.push({
                x: data.time,
                y: data.E,
                name: 'Экспонированные (E)',
                line: { 
                    color: colors.E, 
                    width: 3,
                    shape: 'spline',
                    smoothing: 1.3
                },
                type: 'scatter'
            });
        }
        
        traces.push({
            x: data.time,
            y: data.I,
            name: 'Инфицированные (I)',
            line: { 
                color: colors.I, 
                width: 3,
                shape: 'spline',
                smoothing: 1.3
            },
            type: 'scatter'
        });
        
        traces.push({
            x: data.time,
            y: data.R,
            name: 'Выздоровевшие (R)',
            line: { 
                color: colors.R, 
                width: 3,
                shape: 'spline',
                smoothing: 1.3
            },
            type: 'scatter'
        });
        
        // Компонент D присутствует только в SEIRD модели
        if (model === 'SEIRD') {
            traces.push({
                x: data.time,
                y: data.D,
                name: 'Погибшие (D)',
                line: { 
                    color: colors.D, 
                    width: 3,
                    shape: 'spline',
                    smoothing: 1.3
                },
                type: 'scatter'
            });
        }
        
        // Настройки графика
        const layout = {
            title: {
                text: getModelTitle(model),
                font: { 
                    size: 20, 
                    color: 'var(--foreground)',
                    family: 'Manrope, sans-serif',
                    weight: 700
                }
            },
            font: { 
                family: 'Manrope, sans-serif',
                size: 12
            },
            autosize: true,
            margin: { t: 60, r: 30, b: 50, l: 60 },
            xaxis: {
                title: {
                    text: 'Время (дни)',
                    font: { size: 14 }
                },
                gridcolor: 'rgba(0,0,0,0.1)',
                zerolinecolor: 'rgba(0,0,0,0.2)'
            },
            yaxis: {
                title: {
                    text: 'Количество индивидов',
                    font: { size: 14 }
                },
                gridcolor: 'rgba(0,0,0,0.1)',
                zerolinecolor: 'rgba(0,0,0,0.2)'
            },
            plot_bgcolor: 'rgba(255,255,255,0)',
            paper_bgcolor: 'rgba(255,255,255,0)',
            hovermode: 'closest',
            showlegend: false,
            transition: {
                duration: 500,
                easing: 'cubic-in-out'
            }
        };
        
        // Конфигурация взаимодействия с графиком
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
            displaylogo: false,
            toImageButtonOptions: {
                format: 'png',
                filename: `model-${model.toLowerCase()}`,
                height: 600,
                width: 1200,
                scale: 2
            }
        };
        
        // Отрисовка графика с анимацией
        Plotly.newPlot('plotDiv', traces, layout, config).then(() => {
            // Удаляем спиннер после отрисовки графика
            const chartContainer = document.getElementById('plotDiv');
            // Если вдруг спиннер остался (например, Plotly не полностью перезаписал innerHTML)
            const spinner = chartContainer.querySelector('.loading-spinner');
            if (spinner) spinner.remove();
        });
    }
    
    // Функция для получения заголовка модели
    function getModelTitle(model) {
        return `Модель ${model}`;
    }
    
    // Сводки по математической реализации для каждой модели
    const modelSummaries = {
        SIR: `
            <div class="summary-title">Математическая модель SIR</div>
            <div class="summary-eq">
                \\[
                \\begin{aligned}
                \\frac{dS}{dt} &= -\\beta \\frac{S I}{N} \\\\
                \\frac{dI}{dt} &= \\beta \\frac{S I}{N} - \\gamma I \\\\
                \\frac{dR}{dt} &= \\gamma I
                \\end{aligned}
                \\]
            </div>
            <div class="summary-desc">
                <b>S</b> — восприимчивые, <b>I</b> — инфицированные, <b>R</b> — выздоровевшие.<br>
                <b>β</b> — скорость заражения, <b>γ</b> — скорость выздоровления, <b>N</b> — размер популяции.
            </div>
        `,
        SEIR: `
            <div class="summary-title">Математическая модель SEIR</div>
            <div class="summary-eq">
                \\[
                \\begin{aligned}
                \\frac{dS}{dt} &= -\\beta \\frac{S I}{N} \\\\
                \\frac{dE}{dt} &= \\beta \\frac{S I}{N} - \\sigma E \\\\
                \\frac{dI}{dt} &= \\sigma E - \\gamma I \\\\
                \\frac{dR}{dt} &= \\gamma I
                \\end{aligned}
                \\]
            </div>
            <div class="summary-desc">
                <b>E</b> — экспонированные (инкубационный период), <b>σ</b> — скорость перехода из E в I.<br>
                Остальные параметры аналогичны SIR.
            </div>
        `,
        SEIRD: `
            <div class="summary-title">Математическая модель SEIRD</div>
            <div class="summary-eq">
                \\[
                \\begin{aligned}
                \\frac{dS}{dt} &= -\\beta \\frac{S I}{N} \\\\
                \\frac{dE}{dt} &= \\beta \\frac{S I}{N} - \\sigma E \\\\
                \\frac{dI}{dt} &= \\sigma E - \\gamma I - \\mu I \\\\
                \\frac{dR}{dt} &= \\gamma I \\\\
                \\frac{dD}{dt} &= \\mu I
                \\end{aligned}
                \\]
            </div>
            <div class="summary-desc">
                <b>D</b> — погибшие, <b>μ</b> — коэффициент летальности.<br>
                Остальные параметры аналогичны SEIR.
            </div>
        `
    };

    // Функция для обновления сводки по модели
    function updateModelSummary() {
        const selectedModel = getSelectedModel();
        const summaryDiv = document.getElementById('modelSummary');
        summaryDiv.innerHTML = modelSummaries[selectedModel] || '';
        if (window.MathJax && window.MathJax.typesetPromise) {
            // Очищаем предыдущие формулы и заново рендерим только новый блок
            MathJax.typesetClear([summaryDiv]);
            MathJax.typesetPromise([summaryDiv]);
        }
    }
    
    // Инициализация страницы
    function initPage() {
        updateModelAvailability();
        updateLegendVisibility();
        updateChart();
        updateModelSummary();
    }
    
    // Добавляем анимацию появления
    document.querySelector('.app-header').classList.add('fade-in');
    document.querySelector('.control-section').classList.add('fade-in');
    document.querySelector('.visualization-section').classList.add('fade-in');
    
    // Запускаем инициализацию
    initPage();
});
