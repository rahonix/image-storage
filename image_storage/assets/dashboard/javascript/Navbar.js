import React from 'react';
const Navbar = function(props) {
    return (
        <nav className="navbar navbar-expand-lg navbar-light border-bottom">
            <div className="container-fluid justify-content-between">
                { props.phoneMode ? 
                <button onClick={() => props.onToggleClick()} className="navbar-toggler" type="button" data-toggle="collapse" >
                  <span className="navbar-toggler-icon"></span>
                </button>
                :
                <span onClick={() => props.onToggleClick()} className={props.open ? "bi bi-arrow-bar-left": "bi bi-arrow-bar-right"}>
                </span>
                }
                <p className="text-white"> Invisible! </p>
            </div>
            
        </nav>
    )
}

export default Navbar;