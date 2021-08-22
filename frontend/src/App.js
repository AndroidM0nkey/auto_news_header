import axios from "axios";
import React, { Component } from "react";
import "./App.css";

const URL_REGEXP = /^https?:\/\/(www\.)?interfax.ru/;
const BASE_API_URL = "http://localhost:8000";

class App extends Component {
	constructor(props) {
		super(props);

		this.state = {
			links: [],
			selectedFile: null,
			data: null
		};

		this.submitFile = this.submitFile.bind(this);
		this.onFileChange = this.onFileChange.bind(this);
		this.addLink = this.addLink.bind(this);
		this.removeLink = this.removeLink.bind(this);
		this.onLinkInputChange = this.onLinkInputChange.bind(this);
		this.onLinksSubmit = this.onLinksSubmit.bind(this);
	}

	submitFile(e) {
		e.preventDefault();

		if (!this.state.selectedFile) {
			alert("Не выбран файл для загрузки");
			return;
		}

		const formData = new FormData();

		formData.append("File", this.state.selectedFile);
		formData.append("type", "json");

		axios
			.post(`${BASE_API_URL}`, formData, {
				headers: {
					"Content-Type": "application/json"
				}
			})
			.then(({ data }) =>
				this.setState({ data: data.results.reverse() })
			);
	}

	onFileChange(e) {
		this.setState({ selectedFile: e.target.files[0] });
	}

	addLink() {
		this.setState((state) => {
			let links = Object.assign([], state.links);
			links.push(["", false]);

			return { links };
		});
	}

	removeLink(removeIndex) {
		this.setState((state) => {
			return {
				links: state.links.filter((_, index) => index !== removeIndex)
			};
		});
	}

	onLinkInputChange(e, index) {
		this.setState((state) => {
			state.links[index] = [
				e.target.value,
				URL_REGEXP.test(e.target.value)
			];

			return {
				links: state.links
			};
		});
	}

	onLinksSubmit() {
		if (this.state.links.reduce((prev, curr) => prev && curr, true)) {
			const links = this.state.links.map((val) => val[0]);

			axios
				.post(
					BASE_API_URL,
					{ type: "link", data: links },
					{ headers: { "Content-Type": "application/json" } }
				)
				.then(({ data }) =>
					this.setState({ data: data.results.reverse() })
				);
		}
	}

	render() {
		return (
			<div className="App">
				<div className="links-upload">
					<h3>Используйте ссылки на статьи</h3>
					<div>
						{this.state.links.map((value, index) => {
							return (
								<div key={index} className="input-container">
									<input
										onChange={(e) =>
											this.onLinkInputChange(e, index)
										}
										value={value[0]}
										className={value[1] ? "" : "incorrect"}
									/>
									<button
										onClick={() => this.removeLink(index)}
									>
										X
									</button>
								</div>
							);
						})}
					</div>
					<div className="links-buttons">
						<button className="add-link-btn" onClick={this.addLink}>
							+
						</button>
						<button
							className={`submit-links-btn ${
								this.state.links.length > 0 ? "" : "hidden"
							}`}
							onClick={this.onLinksSubmit}
						>
							Отправить
						</button>
					</div>
					<div className="results">
						{this.state.data &&
							this.state.data.map((entry, index) => {
								return (
									<div>
										<p key={`result-${index}`}>
											{entry[0]} - <span>{entry[1]}</span>
										</p>
										<hr />
									</div>
								);
							})}
					</div>
				</div>
			</div>
		);
	}
}

export default App;
