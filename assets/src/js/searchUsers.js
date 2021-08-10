const searchField = document.querySelector("#searchField");
const usersTable = document.querySelector("#searched-users");
const noResults = document.querySelector('.noResults')

usersTable.style.display = "none";

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    if (searchValue.trim().length > 0) {
        usersTable.style.display = "block";
        usersTable.innerHTML = "";
        console.log("search value:", searchValue);
        fetch("/search-users/", {
            body: JSON.stringify({searchText: searchValue}),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data);
                if (data.length == 0) {
                    console.log('iya');
                    usersTable.innerHTML += `<h1 class="noResults">No results 😞</h1>`
                } else {
                    data.forEach(user => {
                        usersTable.innerHTML += `
                            <a class="user text-dark" href="/accounts/profile/${user.username}/">
                                <img src="${user.photo}" class="s_user_img" alt="">
                                <div>
                                    <h3>${user.username}</h3>
                                    <h3 class="tx-grey f-w-500">${user.first_name} ${user.last_name}</h3>
                                </div>
                            </a>
                        `
                    })
                }

            })
    } else{
        usersTable.style.display = "none";
    }
})