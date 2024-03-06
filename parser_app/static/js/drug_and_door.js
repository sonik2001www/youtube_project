    $(function() {

        // Функція для видалення колонки та пов'язаних записів
        function deleteColumn(colId) {
            $.ajax({
                type: "POST",
                url: "/delete_column/",
                data: { col_id: colId },
                success: function() {
                    // Позиції оновлено успішно
                    console.log("Колонка видалена успішно!");
                    location.reload(); // Оновити сторінку для поновлення даних
                },
                error: function(xhr, status, error) {
                    console.error("Помилка при видаленні колонки:", error);
                }
            });
        }


        $(".container").sortable({
            update: function(event, ui) {
                // Отримуємо новий порядок колонок
                var columnOrder = [];
                $(".col-container").each(function() {
                    columnOrder.push($(this).data("col-id"));
                });

                // Виконуємо AJAX-запит на сервер для оновлення позицій у базі даних
                $.ajax({
                    type: "POST",
                    url: "/update_column_positions/",
                    data: { order: columnOrder.join(",") },
                    success: function() {
                        console.log("Позиції оновлено успішно!");

                        // Після успішного оновлення позицій, здійснюємо сортування полів у кожній колонці
                        $(".sortable-list").each(function() {
                            Sortable.create(this, {
                                group: 'sales',
                                animation: 150
                            });
                        });
                    },
                    error: function(xhr, status, error) {
                        console.error("Помилка при оновленні позицій:", error);
                    }
                });
            }
        });


        // Обробник події для натискання на хрестик колонки
        $(document).on('click', '.delete-button', function() {
            var elementId = $(this).data("col-id");
            deleteColumn(elementId);
        });

        // Включаємо сортування для списків полів (sortable-list)
        $(".sortable-list").sortable({
            connectWith: ".sortable-list",
            update: function(event, ui) {
                var colId = ui.item.closest(".col-container").data("col-id");
                var fieldId = ui.item.data("field-id");
                var newPosition = ui.item.index() + 1;

                console.log(fieldId)

                // Виконуємо AJAX-запит на сервер для збереження змін в базі даних
                $.ajax({
                    type: "POST",
                    url: "/move_field/",
                    data: { col_id: colId, field_id: fieldId, new_position: newPosition},
                    success: function() {
                        console.log("Поле переміщено успішно!");
                    },
                    error: function(xhr, status, error) {
                        console.error("Помилка при переміщенні поля:", error);
                    }
                });
            }
        });

        // Обробник події для натискання на хрестик поля
        $(document).on('click', '.sortable-list .delete-button', function(event) {
            event.stopPropagation(); // Зупинити спливання події до батьківського елементу
            var elementId = $(this).data("field-id");
            deleteField(elementId);
        });

        // Функція для видалення поля
        function deleteField(fieldId) {
            $.ajax({
                type: "POST",
                url: "/delete_field/",
                data: { field_id: fieldId },
                success: function() {
                    console.log("Поле видалено успішно!");
                    location.reload(); // Оновити сторінку для поновлення даних
                },
                error: function(xhr, status, error) {
                    console.error("Помилка при видаленні поля:", error);
                }
            });
        }

        // Показати форму для додавання поля при натисканні на плюсик
        $(".add-button").click(function() {
            // Знаходимо батьківський елемент (колонку)
            var colContainer = $(this).closest(".col-container");

            // Показуємо форму
            colContainer.find(".field-form").show();
        });

        // Додати нове поле при натисканні на кнопку Add
        $(".add-field-button").click(function() {
            // Знаходимо батьківський елемент (колонку)
            var colContainer = $(this).closest(".col-container");

            // Отримуємо значення з полів вводу
            var nameValue = colContainer.find(".name-input").val();
            var priceValue = colContainer.find(".price-input").val();

            if (priceValue === '') {
                priceValue = ' ';
            }

            // Виконуємо AJAX-запит на сервер для додавання поля
            $.ajax({
                type: "POST",
                url: "/add_field/",
                data: { col_id: colContainer.data("col-id"), name: nameValue, price: priceValue},
                success: function() {
                    console.log("Поле додано успішно!");
                    location.reload(); // Оновити сторінку для поновлення даних
                },
                error: function(xhr, status, error) {
                    console.error("Помилка при додаванні поля:", error);
                }
            });
        });


        // Функція для відображення зірочок залежно від значення stars
        function displayStars(stars, container) {
            container.find(".star").each(function(index) {
                if (index < stars) {
                    $(this).addClass("filled");
                } else {
                    $(this).removeClass("filled");
                }
            });
        }

        // Знаходить всі контейнери з класом "stars-container" і відображає зірочки
        $(".stars-container").each(function() {
            var stars = parseInt($(this).data("stars"));
            displayStars(stars, $(this));
        });

        // Обробник події для кліку на зірки
        $(".star").on("click", function() {
            var starsContainer = $(this).closest(".stars-container");
            var stars = parseInt(starsContainer.data("stars"));
            var clickedStarIndex = $(this).index();

            // Змінюємо значення в залежності від того, яку зірку клікнули
            if (clickedStarIndex < stars) {
                stars = 0;
            } else {
                stars = clickedStarIndex + 1;
            }

            // Виконуємо AJAX-запит на сервер для оновлення значення поля "stars" в базі даних
            $.ajax({
                type: "POST",
                url: "/update_stars/",
                data: { field_id: starsContainer.data("field-id"), stars: stars },
                success: function() {
                    console.log("Кількість зірочок оновлено успішно!");

                    // Оновлюємо значення stars в starsContainer після успішного AJAX-запиту
                    starsContainer.data("stars", stars);

                    // Відображаємо зірочки з оновленим значенням
                    displayStars(stars, starsContainer);
                },
                error: function(xhr, status, error) {
                    console.error("Помилка при оновленні кількості зірочок:", error);
                }
            });
        });
    });

$(document).ready(function() {
    // Показати форму для додавання нової колонки при натисканні на плюсик
    $(document).on('click', '.add-col-button', function() {
        var container = document.getElementById('last-container');
        document.getElementById('column-form').style.display = 'block';
    });

    // Додати нову колонку при натисканні на кнопку Add
    $(document).on('click', '.add-column-button', function() {
        var container = document.getElementById('last-container');
        var nameValue = document.getElementById('column-name-input').value;

        $.ajax({
            type: "POST",
            url: "/add_column/",
            data: { name: nameValue },
            success: function() {
                console.log("Колонку додано успішно!");
                location.reload();
            },
            error: function(xhr, status, error) {
                console.error("Помилка при додаванні колонки:", error);
            }
        });
    });
});