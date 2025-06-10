const Header = () => {
  return (
    <div className="flex p-2 shadow-lg justify-between">
      <div className="w-[10%] cursor-pointer">
        <img className="h-12" src="/src/assets/logo.png" alt="logo" />
      </div>
      <div className="flex justify-center items-center">
        <ul className="flex">
          <li className="m-1 cursor-pointer bg-gray-200 px-2 rounded-lg shadow-lg hover:bg-white">
            Top rated
          </li>
          <li className="m-1 cursor-pointer bg-gray-200 px-2 rounded-lg shadow-lg hover:bg-white">
            Latest
          </li>
          <li className="m-1 cursor-pointer bg-gray-200 px-2 rounded-lg shadow-lg hover:bg-white">
            Anime
          </li>
          <li className="m-1 cursor-pointer bg-gray-200 px-2 rounded-lg shadow-lg hover:bg-white">
            Bollywood
          </li>
        </ul>
      </div>
      <div className="flex justify-around w-[10%] items-center">
        <img
          className="h-8 w-8 cursor-pointer"
          src="/src/assets/avatar.svg"
          alt="user icon"
        />
        <span className="cursor-pointer">Username</span>
      </div>
    </div>
  );
};

export default Header;
