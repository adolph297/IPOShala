const TabLoader = ({ text = "Loading..." }) => {
  return (
    <div className="py-8 text-center text-gray-500 text-sm">
      {text}
    </div>
  );
};

export default TabLoader;
