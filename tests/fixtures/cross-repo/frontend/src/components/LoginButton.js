export function LoginButton() {                                                                                                             
    async function handleAuth() {                                                                                                           
        const response = await fetch('/auth/login', {  // Direct path match                                                                     
            method: 'POST',                                                                                                                     
            body: JSON.stringify({ username: 'test', password: 'test' })                                                                        
        });                                                                                                                                
        return response.json();                                                                                                             
    }                                                                                                                                       
                                                                                                                                            
    return <button onClick={handleAuth}>Login</button>;                                                                                     
} 