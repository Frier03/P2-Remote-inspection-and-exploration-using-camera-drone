function trimAccessToken(token){
    let fixedToken = token.split('access_token=')[1]
    fixedToken = fixedToken.split(';')[0]
    return fixedToken
}

export default trimAccessToken;