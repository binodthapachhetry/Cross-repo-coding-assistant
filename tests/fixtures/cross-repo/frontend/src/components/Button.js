export function handleAuth() {                                                                                                              
    fetch('/api/login', {  // Should match backend endpoint                                                                                   
    method: 'POST',                                                                                                                         
    body: JSON.stringify({ username, password })                                                                                            
} 