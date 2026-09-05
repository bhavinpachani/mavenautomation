// /** @odoo-module **/
// import { Chatter } from "@mail/chatter/web_portal/chatter";
// import { patch } from "@web/core/utils/patch";
// import { ControlPanel } from "@web/search/control_panel/control_panel";
// import { _t } from "@web/core/l10n/translation";
// import { rpc } from '@web/core/network/rpc';

// patch(Chatter.prototype, {  
//     async setup() {
//         if (super.setup) {
//             await super.setup(...arguments);
//         }
//         console.log("Chatter setup called in Odoo 18");  
//         this.toggleChatterVisibility();
//     },

//     async toggleChatterVisibility() {
//         try {
//             // Verify if the RPC call structure is still valid in Odoo 18
//             const userSpecificData = await rpc("/web/dataset/call_kw", {
//                 model: "res.users",
//                 method: "get_chatter_toggle_flag",
//                 args: [],
//                 kwargs: {},
//             }).catch(error => {
//                 console.error("RPC Error (User Specific): ", error);
//                 return {};
//             });

//             const groupSpecificData = await rpc("/web/dataset/call_kw", {
//                 model: "res.users",
//                 method: "get_chatter_toggle_group_flag",
//                 args: [],
//                 kwargs: {},
//             }).catch(error => {
//                 console.error("RPC Error (Group Specific): ", error);
//                 return {};
//             });

//             console.log("User Data:", userSpecificData);
//             console.log("Group Data:", groupSpecificData);

//             // Ensure element existence
//             const chatterToggleButton = document.querySelector("#chatter-toggle");
//             const chatToggleButton = document.querySelector("#toggleChatButton");

//             if (!chatterToggleButton) console.warn("chatter-toggle button not found in Odoo 18");
//             if (!chatToggleButton) console.warn("toggleChatButton not found in Odoo 18");

//             // Determine if Chatter should be enabled
//             const isChatterEnabled = 
//                 (userSpecificData && userSpecificData.enable_chatter_button === 1) || 
//                 (groupSpecificData && groupSpecificData.enable_chatter_group === 1);

//             if (isChatterEnabled) {
//                 if (chatterToggleButton) chatterToggleButton.style.display = "inline-block";
//                 if (chatToggleButton) chatToggleButton.style.display = "inline-block";
//             } else {
//                 if (chatterToggleButton) chatterToggleButton.style.display = "none";
//                 if (chatToggleButton) chatToggleButton.style.display = "none";
//             }
//         } catch (error) {
//             console.error("Error toggling chatter visibility:", error);
//         }
//     },

//     toggleChatter() {
//         const chatterElement = document.querySelector('.o-mail-ChatterContainer');
//         const showChatterButton = document.querySelector('#history_btn'); 
//         const hideChatterButton = document.querySelector('button[title="Hide Chatter"]'); 

//         if (chatterElement) {
//             chatterElement.classList.add('d-none'); 
//         }

//         if (hideChatterButton) {
//             hideChatterButton.classList.add('d-none'); 
//         }

//         if (showChatterButton) {
//             showChatterButton.classList.remove('d-none'); 
//         }
//     },    

//     toggleChat() {
//         const chatterElement = document.querySelector('.o-mail-Thread');
//         const toggleIcon = document.querySelector('#chatterToggleIcon');

//         if (chatterElement) {
//             chatterElement.classList.toggle('d-none');

//             if (toggleIcon) {
//                 if (chatterElement.classList.contains('d-none')) {
//                     toggleIcon.classList.remove('fa-eye-slash');
//                     toggleIcon.classList.add('fa-eye');
//                 } else {
//                     toggleIcon.classList.remove('fa-eye');
//                     toggleIcon.classList.add('fa-eye-slash');
//                 }
//             } else {
//                 console.error("Chatter toggle icon not found!");
//             }
//         } else {
//             console.error("Chatter element not found!");
//         }
//     }
// });

// patch(ControlPanel.prototype, {   
//     toggleChattershow() {
//         const chatterElement = document.querySelector('.o-mail-ChatterContainer');
//         const showChatterButton = document.querySelector('#history_btn');
//         const hideChatterButton = document.querySelector('button[title="Hide Chatter"]'); 

//         if (chatterElement) {
//             chatterElement.classList.remove('d-none'); 
//         }

//         if (showChatterButton) {
//             showChatterButton.classList.add('d-none'); 
//         }

//         if (hideChatterButton) {
//             hideChatterButton.classList.remove('d-none'); 
//         }
//     }
// });



/** @odoo-module **/
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { _t } from "@web/core/l10n/translation";
import { rpc } from '@web/core/network/rpc';

patch(Chatter.prototype, {  
    
    async setup() {
        super.setup(...arguments);
        console.log("Chatter setup called");  
        this.toggleChatterVisibility();
    },

    async toggleChatterVisibility() {
        try {
           
            const userSpecificData = await rpc("/web/dataset/call_kw/res.users/get_chatter_toggle_flag", {
                model: "res.users",
                method: "get_chatter_toggle_flag",
                args: [],
                kwargs: {},
            });
            const groupSpecificData = await rpc("/web/dataset/call_kw/res.users/get_chatter_toggle_group_flag", {
                model: "res.users",
                method: "get_chatter_toggle_group_flag",
                args: [],
                kwargs: {},
            });

            // const chatterToggleButton = document.getElementById("chatter-toggle");
            // const chatToggleButton = document.getElementById("toggleChatButton");

            
            // const isChatterEnabled = 
            //     userSpecificData.enable_chatter_button === 1 || 
            //     groupSpecificData.enable_chatter_group === 1;

            // if (isChatterEnabled) {
            //     if (chatterToggleButton) chatterToggleButton.style.display = "inline-block";
            //     if (chatToggleButton) chatToggleButton.style.display = "inline-block";
            // } else {
            //     if (chatterToggleButton) chatterToggleButton.style.display = "none";
            //     if (chatToggleButton) chatToggleButton.style.display = "none";
            // }

            const chatterToggleButton = document.getElementById("chatter-toggle");
            const chatToggleButton = document.getElementById("toggleChatButton");
    
            const isChatterEnabled = 
                userSpecificData.enable_chatter_button === 1 || 
                groupSpecificData.enable_chatter_group === 1;
    
            if (isChatterEnabled) {
                if (chatterToggleButton) chatterToggleButton.classList.add("chatter-visible");
                if (chatToggleButton) chatToggleButton.classList.add("chatter-visible");
            }
            

            
            
        } catch (error) {
            console.error("Error toggling chatter visibility:", error);
        }
    },

    toggleChatter() {
        const chatterElement = document.querySelector('.o-mail-ChatterContainer');
        const showChatterButton = document.querySelector('#history_btn'); // Show Chatter button
        const hideChatterButton = document.querySelector('button[title="Hide Chatter"]'); // Hide Chatter button
    
        // Hide chatter element
        if (chatterElement) {
            chatterElement.classList.add('d-none'); // Hide chatter
        }
    
        // Hide "Hide Chatter" button and show "Show Chatter" button
        if (hideChatterButton) {
            hideChatterButton.classList.add('d-none'); // Hide "Hide Chatter" button
        }
    
        if (showChatterButton) {
            showChatterButton.classList.remove('d-none'); // Show "Show Chatter" button
        }
    }      
    ,    
    toggleChat() {
        const chatterElement = document.querySelector('.o-mail-Thread');
        const toggleIcon = document.querySelector('#chatterToggleIcon'); // Using querySelector to find by ID
        const toggleButton = document.querySelector('#toggleChatButton');
    
        if (chatterElement) {
            // Toggle the visibility of the Chatter
            chatterElement.classList.toggle('d-none');
    
            if (toggleIcon) {
                // Change the icon based on the visibility of Chatter
                if (chatterElement.classList.contains('d-none')) {
                    // If Chatter is hidden, show 'fa-eye' icon
                    toggleIcon.classList.remove('fa-eye-slash');
                    toggleIcon.classList.add('fa-eye');
                    toggleButton.title = "Show Chat";
                } else {
                    // If Chatter is visible, show 'fa-eye-slash' icon
                    toggleIcon.classList.remove('fa-eye');
                    toggleIcon.classList.add('fa-eye-slash');
                    toggleButton.title = "Hide Chat";
                }
            } else {
                console.error("Chatter toggle icon not found!");
            }
        } else {
            console.error("Chatter element not found!");
        }
    }
    
    
});

patch(ControlPanel.prototype, {   
    toggleChattershow() {
    
        const chatterElement = document.querySelector('.o-mail-ChatterContainer');
        const showChatterButton = document.querySelector('#history_btn'); // Show Chatter button
        const hideChatterButton = document.querySelector('button[title="Hide Chatter"]'); // Hide Chatter button
    
        // Show chatter element
        if (chatterElement) {
            chatterElement.classList.remove('d-none'); // Show chatter
        }
    
        // Hide "Show Chatter" button
        if (showChatterButton) {
            showChatterButton.classList.add('d-none'); // Hide "Show Chatter" button
        }
    
        // Show "Hide Chatter" button
        if (hideChatterButton) {
            hideChatterButton.classList.remove('d-none'); // Show "Hide Chatter" button
        }
    }
});