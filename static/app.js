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
    $(this).parent().remove()
}

// //Adding ingredients to grocery list
// $('.ingredient-add').click(addToList)
// async function addToList(){
//     const ingredient = $(this).data('ingredient')
//     const user_id = $(this).data('user_id')
//     await axios.post(`/users/${user_id}/shopping-list`)
//}
