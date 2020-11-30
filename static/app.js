//Todo Functions
$('.delete-todo').click(deleteTodo)
async function deleteTodo(){
    const id = $(this).data('id')
    const user = $(this).data('user')
    await axios.post(`/users/${user}/shopping-list/${id}/delete`)
    $(this).parent().remove()
}

//Saved Meals
$('.delete-saved-meals').click(deleteMeal)
async function deleteMeal(){
    const meal_id = $(this).data('meal_id')
    const user_id = $(this).data('user_id')
    await axios.post(`/users/${user_id}/saved-meals/${meal_id}/delete`)
    $(this).parent().remove()
}