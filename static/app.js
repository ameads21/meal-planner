//Todo Functions
$('.delete-todo').click(deleteTodo)
async function deleteTodo(){
    const id = $(this).data('id')
    const user = $(this).data('user')
    await axios.post(`/users/${user}/shopping-list/${id}/delete`)
    $(this).parent().remove()
}

$('.todo-item').click(markTodo)
async function markTodo(){
    const id = $(this).siblings('.delete-todo').data('id')
    const user = $(this).siblings('.delete-todo').data('user')
    await axios.post(`/users/${user}/shopping-list/${id}`)
    $(this).siblings('.todo-text').toggleClass('checked')
}

$('.ingredient-add').click(addTodo)
async function addTodo(){
    const ingredient = $(this).data('ingredient')
    const user_id = $(this).data('user_id')
    data = {
        "ingredient": ingredient,
        "user_id": user_id
    }
    await axios.post(`/users/${user_id}/shopping-list/add`, data)
    $(this).parent().append('<p>Added to grocery list!</p>')
}

//Adding Saved Meals
async function saveMeal(evt){
    evt.preventDefault()
    $('#submitBtn').attr('disabled', true)
    data = {
        "user_id": $('#submitBtn').data('user_id'),
        "meal_id": $('#submitBtn').data('meal_id'),
        "meal_name": $('#submitBtn').data('meal_name'),
        "meal_image": $('#submitBtn').data('meal_image')
    }
    await axios.post(`/users/${data.user_id}/meals/${data.meal_id}/view/${data.meal_name}`, data)
    $('#save-meal-form').html('<h4>Meal added to saved meals</h4>');
}
$('#save-meal-form').on("submit", saveMeal);


//Deleting Saved Meals
$('.delete-saved-meals').click(deleteMeal)
async function deleteMeal(){
    const meal_id = $(this).data('meal_id')
    const user_id = $(this).data('user_id')
    await axios.post(`/users/${user_id}/saved-meals/${meal_id}/delete`)
    $(`#${meal_id}`).remove();
}

if (window.location.pathname == '/'){
    $('#container').removeClass('container')
    $('#container').removeAttr('style')
    $('#container').css("height", "100%")
}

//Calendar
user_id = document.querySelector('p').innerText
table = false
let today = new Date()
let month = today.getMonth() + 1;
let year = today.getFullYear();
if (window.location.pathname == `/users/${user_id}/calendar`){
    table = true
    genearateCalendar()
}
async function genearateCalendar(){
    $('.calendarDiv').html('<div class="d-flex justify-content-center spinner"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>')
    data = {
        "month": month,
        "year": year
    }
    
    calendar = await axios.post(`/users/${user_id}/calendar`, data)
    $('.spinner').remove();
    $('.container').append(`${calendar['data']['calendar']}`)
    $('table').addClass('table table-striped')
    $('.month').addClass('text-center')
    header = document.querySelector('th')
    header.innerHTML = `<button id="backward-month" onclick="previousMonth()"> < </button> ${header.innerText} <button id="forward-month" onclick="nextMonth()"> > </button>`
    addLinks(month, year)
    addData(calendar['data']['meals'])
}

function addLinks(month, year){
    allTd = document.querySelectorAll('td')
    for (d of allTd){
        if (d.innerText != String.fromCharCode(160)){
            d.innerHTML = `<div>${d.innerText}<ul class="list-group list-group-flush" id="day-${d.innerText}"></ul></div>`
        }
    }
}
function addData(data){
    numMeals = 0
    for (d of data){
        dateSplit = d.date.split('-')
        day = dateSplit[dateSplit.length - 1]
        if (d.meal_id != null)
        {
            $(`<li class="meal_info list-group-item text-center"><button class="close meal_info list-group-item " id="meal_${numMeals}" onclick="delete_calendar_meal(${d.user_id},${d.id}, '${d.date}', ${numMeals})" aria-label="Close"><span aria-hidden="true">&times;</span></button><a href="/users/${d.user_id}/meals/${d.meal_id}/view/${d.meal_name}">${d.meal_name}</a></li>`).appendTo($(`#day-${Number(day)}`))
        } else {
            $(`<li class="meal_info list-group-item text-center"><button class="close" id="meal_${numMeals}" onclick="delete_calendar_meal(${d.user_id},${d.id},'${d.date}', ${numMeals})" aria-label="Close"><span aria-hidden="true">&times;</span></button>${d.meal_name}</li>`).appendTo($(`#day-${Number(day)}`))
        }
        numMeals += 1;
    }
}

function nextMonth(){
    month += 1;
    if (month >= 13){
        month = 1;
        year += 1;
    }
    $("table").remove();
    genearateCalendar()
}

function previousMonth(){
    month -= 1;
    if (month <= 0){
        month = 12;
        year -= 1;
    }
    $("table").remove();
    genearateCalendar()
}

async function delete_calendar_meal(user_id, id, date, meal_num){
    await axios.post(`/users/${user_id}/calendar/delete/${id}`)
    dateSplit = date.split('-')
    day = dateSplit[dateSplit.length - 1]
    $(`#meal_${meal_num}`).closest("li").remove()
}