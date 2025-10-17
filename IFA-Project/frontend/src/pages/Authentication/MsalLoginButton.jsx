import React from "react";
import { useMsal } from "@azure/msal-react";

const MsalLoginButton = () => {
    const { instance } = useMsal();

    const handleLogin = () => {
        instance.loginPopup({
            scopes: ["user.read"], // Replace with required scopes
        }).catch(e => {
            console.error(e);
        });
    };

    return <button onClick={handleLogin}>Login</button>;
};

export default MsalLoginButton;
